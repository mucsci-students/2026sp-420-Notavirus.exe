# controllers/undoRedo_controller.py
from typing import Optional

class UndoRedoController:
    """
    Manages the Undo and Redo stacks for the application.
    Since the application's config is global and lives in memory, we can track
    history using instance variables. This avoids NiceGUI context errors and
    persists smoothly across page navigations.
    """
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
        self.last_known_state = None

    def set_initial_state(self, initial_state_json: str):
        """
        Sets the baseline state when a new configuration is loaded.
        """
        self.last_known_state = initial_state_json
        self.clear()

    def record_state(self, current_state_json: str):
        """
        Pushes the last known state to the undo stack, updates the last known state,
        and clears the redo stack.
        """
        try:
            from scheduler import CombinedConfig
            last_cfg = CombinedConfig.model_validate_json(self.last_known_state) if self.last_known_state else None
            curr_cfg = CombinedConfig.model_validate_json(current_state_json) if current_state_json else None
            last = last_cfg.model_dump() if last_cfg else None
            curr = curr_cfg.model_dump() if curr_cfg else None
            is_different = last != curr
        except Exception:
            is_different = self.last_known_state != current_state_json
            
        if self.last_known_state and is_different:
            self.undo_stack.append(self.last_known_state)
            self.redo_stack.clear()
            
        self.last_known_state = current_state_json

    def undo(self, current_state_json: str) -> Optional[str]:
        """
        Pops the last state from the undo stack, pushes the current state to the redo stack,
        and returns the popped state for restoration.
        """
        if not self.undo_stack:
            return None
            
        previous_state = self.undo_stack.pop()
        self.redo_stack.append(current_state_json)
        self.last_known_state = previous_state
        return previous_state

    def redo(self, current_state_json: str) -> Optional[str]:
        """
        Pops the next state from the redo stack, pushes the current state to the undo stack,
        and returns the popped state for restoration.
        """
        if not self.redo_stack:
            return None
            
        next_state = self.redo_stack.pop()
        self.undo_stack.append(current_state_json)
        self.last_known_state = next_state
        return next_state
        
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0
        
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
        
    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
