# control/fsm_implementation.py

class FSMArrayImpl:
    """基于二维数组的有限状态机（对应 PPT 图3.56）"""
    def __init__(self, states, events):
        self.states = {s: i for i, s in enumerate(states)}
        self.events = {e: i for i, e in enumerate(events)}
        self.transition_table = [[None] * len(events) for _ in range(len(states))]

    def register_transition(self, state, event, next_state, action):
        s_idx = self.states[state]
        e_idx = self.events[event]
        self.transition_table[s_idx][e_idx] = (next_state, action)

    def handle_event(self, current_state, event):
        s_idx = self.states[current_state]
        e_idx = self.events[event]
        entry = self.transition_table[s_idx][e_idx]
        if entry:
            next_state, action = entry
            if action:
                action()
            return next_state
        return current_state


class FSMMultiTableImpl:
    """基于多级表的有限状态机（对应 PPT 图3.57）"""
    def __init__(self):
        self.state_index_table = {}  # {state: event_table}
        
    def register(self, state, event, next_state, action):
        if state not in self.state_index_table:
            self.state_index_table[state] = {}
        self.state_index_table[state][event] = (next_state, action)
        
    def handle_event(self, state, event):
        event_table = self.state_index_table.get(state, {})
        entry = event_table.get(event)
        if entry:
            next_state, action = entry
            if action:
                action()
            return next_state
        return state