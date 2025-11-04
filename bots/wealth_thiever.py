from bots.core import BotConfigMixin
from bots.core.cfg_types import (
    RangeParam,
    BreakCfgParam,
    RGBParam,
    ItemParam,
)
from core.bot import Bot
from core.logger import get_logger
from core.control import ScriptControl
from core import tools

import time
import random


control = ScriptControl()


class BotConfig(BotConfigMixin):
    # Event detection
    event_tile: RGBParam = RGBParam.from_tuple((255, 0, 255))  # magenta box (#ff00ff)
    color_tolerance: int = 40
    hover_keywords: list[str] = ["pickpocket", "wealth"]  # right-click hover match

    # Timing
    search_interval: float = 0.8  # polling cadence while searching for event
    event_duration_s: int = 20  # expected duration of the pickpocket window
    stall_timeout_s: float = 5.0  # re-click if no progress for this long during event
    event_missing_timeout_s: float = 2.5  # if event tile missing this long during window -> end early
    
    # Inventory
    coin_pouch: ItemParam = ItemParam("Coin pouch")
    # Pouch opening tuning (more forgiving & steady)
    coin_pouch_total_timeout_s: float = 25.0  # overall max time to attempt opening
    coin_pouch_stall_reclick_s: float = 4.0   # if no decrease for this many seconds, force click
    coin_pouch_click_interval: RangeParam = RangeParam(0.18, 0.35)  # steady cadence (no burst)

    # Optional small jitter to feel human
    click_jitter_s: RangeParam = RangeParam(0.15, 0.4)

    # Break configuration
    break_cfg: BreakCfgParam = BreakCfgParam(
        RangeParam(15, 45),
        0.001,
    )


class BotExecutor(Bot):
    name: str = "Wealth Thiever"
    description: str = (
        "Pickpockets Wealthy citizens when the green event tile appears; opens coin pouches after."
    )

    def __init__(self, config: BotConfig, user: str = ""):
        super().__init__(user, break_cfg=config.break_cfg)
        self.cfg: BotConfig = config
        self.log = get_logger("WealthThiever")
        # cache of last pouch MatchResult for faster repeated clicks
        self._cached_pouch_match = None

    def start(self):
        self.main_loop()

    # ----- Main loop -----
    def main_loop(self):
        consecutive_failures = 0
        backoff_base = 0.5
        max_failures = 5

        while True:
            self.control.propose_break()

            # Look for the green event box
            box = self._get_event_box()
            if not box:
                time.sleep(self.cfg.search_interval)
                continue

            try:
                # Attempt to click into the event with bounded retries
                if not self._attempt_click_event(box, max_attempts=5):
                    raise RuntimeError("Unable to start event via click")

                # Run the event window and then open coin pouches
                self._during_event()
                self._open_coin_pouches()

                # Success resets failure count
                consecutive_failures = 0
            except Exception as e:
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    self.log.error(f"Too many errors ({consecutive_failures}); pausing before resuming search: {e}")
                    # brief cooldown before resuming normal search loop
                    time.sleep(6.0 + random.uniform(0.0, 1.0))
                    consecutive_failures = 0  # reset after cooldown
                else:
                    delay = min(8.0, backoff_base * (2 ** (consecutive_failures - 1))) + random.uniform(0, 0.5)
                    self.log.warning(f"Error during event handling; retrying soon ({consecutive_failures}/5). Waiting {delay:.1f}s")
                    time.sleep(delay)

            # After handling, resume searching
            time.sleep(random.uniform(0.2, 0.6))

    # ----- Event handling helpers -----
    @control.guard
    def _get_event_box(self):
        try:
            return tools.find_color_box(
                self.client.get_filtered_screenshot(),
                self.cfg.event_tile,
                tol=self.cfg.color_tolerance,
            )
        except Exception:
            # Not found is expected frequently; just signal no box without logging
            return None

    def _attempt_click_event(self, box, max_attempts: int = 5) -> bool:
        attempts = 0
        while attempts < max_attempts:
            if self._click_event_box(box):
                return True
            attempts += 1
            time.sleep(0.2 + random.uniform(0.0, 0.2))
            # refresh the target box in case it moved slightly
            box = self._get_event_box()
            if not box:
                # event likely disappeared; stop attempts for now
                break
        return False

    @control.guard
    def _click_event_box(self, box) -> bool:
        try:
            clicked = self.client.fast_click_tile(
                self.cfg.event_tile,
                self.cfg.hover_keywords,
                max_time=1.2,
                initial_tolerance=self.cfg.color_tolerance,
                tolerance_growth=4,
                center_lock=True,
                require_hover=True,
                move_speed_px_per_s=4000,
            )
            if not clicked:
                raise RuntimeError("fast_click_tile failed to execute click")
            # small settle move to avoid hover collisions
            self.client.move_to(self.client.window_match)
            return True
        except Exception as e:
            self.log.debug(f"Failed to click event tile: {e}")
            return False

    def _inv_count(self, name: str) -> int:
        try:
            return len(self.client.get_inv_items([name]))
        except Exception as e:
            self.log.debug(f"Inventory count failed for {name}: {e}")
            return 0

    def _during_event(self):
        """While the event runs (~20s), monitor coin pouch gains, attempt re-clicks, and optionally drain pouches inline."""
        start = time.time()
        last_gain = start
        last_event_seen = start
        pouch_name = self.cfg.coin_pouch.name
        prev_cnt = self._inv_count(pouch_name)
        drained_inline = False

        duration_limit = self.cfg.event_duration_s
        stall_limit = self.cfg.stall_timeout_s
        missing_limit = self.cfg.event_missing_timeout_s

        while time.time() - start < duration_limit:
            # pacing jitter (kept small so inline draining remains responsive)
            time.sleep(random.uniform(*self.cfg.click_jitter_s.value))

            current_cnt = self._inv_count(pouch_name)
            if current_cnt > prev_cnt:
                self.log.debug(f"Coin pouch increased: {prev_cnt} -> {current_cnt}")
                prev_cnt = current_cnt
                last_gain = time.time()

                # Inline drain once when first pouches begin accumulating
                if not drained_inline and current_cnt > 0:
                    if self._inline_open_pouches(max_window_s=5.5):
                        drained_inline = True
                        # Update baseline after draining
                        prev_cnt = self._inv_count(pouch_name)

            # Check for event tile presence
            ev_box = self._get_event_box()
            if ev_box:
                last_event_seen = time.time()

            # Re-click attempt if stalled and tile still visible
            if time.time() - last_gain > stall_limit:
                if ev_box:
                    self._click_event_box(ev_box)
                    last_gain = time.time()
                else:
                    self.log.debug("Stall detected but event tile missing; skipping re-click.")

            # Early termination heuristic
            if (
                (time.time() - last_event_seen) > missing_limit
                and (time.time() - last_gain) > stall_limit * 0.6
            ):
                self.log.info("Event appears to have ended early; exiting event loop.")
                break

            self.control.propose_break()

    def _open_coin_pouches(self):
        """Click coin pouches to convert them into coins; retry until they disappear or timeout."""
        pouch = self.cfg.coin_pouch.name
        cnt_before = self._inv_count(pouch)
        if cnt_before <= 0:
            return

        self.log.info(f"Opening {cnt_before} coin pouch(es)...")
        deadline = time.time() + self.cfg.coin_pouch_total_timeout_s
        last_change = time.time()
        prev_cnt = cnt_before
        consecutive_no_change = 0

        # Loop: re-find pouch each click (avoid stale cached match); stop when gone or timeout
        while time.time() < deadline:
            items = self.client.get_inv_items([pouch], x_sort=True, y_sort=True)
            if not items:
                # confirm it's really gone by quick re-count
                if self._inv_count(pouch) == 0:
                    self.log.info("All coin pouches opened.")
                    break
                else:
                    # brief micro-yield then continue
                    time.sleep(0.05)
                    continue

            target = items[0]
            self.client.click(target, click_cnt=1)

            # allow game to register; small sleep based on configured interval lower bound
            time.sleep(random.uniform(self.cfg.coin_pouch_click_interval.value[0], self.cfg.coin_pouch_click_interval.value[0] + 0.05))

            cur_cnt = self._inv_count(pouch)
            if cur_cnt == 0:
                self.log.info("All coin pouches opened.")
                break
            if cur_cnt < prev_cnt:
                self.log.debug(f"Coin pouch count decreased: {prev_cnt} -> {cur_cnt}")
                prev_cnt = cur_cnt
                last_change = time.time()
                consecutive_no_change = 0
            else:
                consecutive_no_change += 1

            # If no change for a while, escalate with a couple rapid extra clicks
            if (time.time() - last_change) > self.cfg.coin_pouch_stall_reclick_s or consecutive_no_change >= 5:
                self.client.click(target, click_cnt=1)
                time.sleep(0.05)
                self.client.click(target, click_cnt=1)
                consecutive_no_change = 0
                # re-evaluate immediately
                cur_cnt2 = self._inv_count(pouch)
                if cur_cnt2 < prev_cnt:
                    self.log.debug(f"Coin pouch count decreased (post-escalation): {prev_cnt} -> {cur_cnt2}")
                    prev_cnt = cur_cnt2
                    last_change = time.time()

        else:
            remaining = self._inv_count(pouch)
            if remaining > 0:
                self.log.warning(f"Timed out opening coin pouches; {remaining} still remain after {self.cfg.coin_pouch_total_timeout_s:.1f}s.")

        # Nudge off the window briefly
        self.client.move_off_window()

    @control.guard
    def _click_pouch_once(self):
        """Single click on cached or freshly located coin pouch match."""
        pouch = self.cfg.coin_pouch.name
        try:
            items = self.client.get_inv_items([pouch], x_sort=True, y_sort=True)
            if not items:
                return
            self.client.click(items[0], click_cnt=1)
        except Exception as e:
            self.log.debug(f"Failed to click coin pouch: {e}")
            # no cache used now; silent recover

    def _inline_open_pouches(self, max_window_s: float = 5.0) -> bool:
        """Rapidly open coin pouches inline during the event window.

        Returns True if inventory reduced to zero, else False (timeout or failure)."""
        start = time.time()
        pouch = self.cfg.coin_pouch.name
        last_change = start
        prev = self._inv_count(pouch)
        if prev <= 0:
            return True
        while time.time() - start < max_window_s:
            self._click_pouch_once()
            time.sleep(0.05)
            cur = self._inv_count(pouch)
            if cur == 0:
                self.log.debug("Inline pouch drain complete.")
                return True
            if cur < prev:
                prev = cur
                last_change = time.time()
            elif time.time() - last_change > 1.5:
                # escalate with a double click
                self._click_pouch_once()
                self._click_pouch_once()
                last_change = time.time()
        self.log.debug("Inline pouch drain incomplete (timeout).")
        return False
