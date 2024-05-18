from typing import Type

from .state import State, NullState
from .context import Context, NullContext
from .transition_table import StateTransitionTable
from . import EventEnum


class FiniteStateMachine:
    def __init__(self, transition_table: StateTransitionTable, initial_state: State = NullState(),
                 context: Context = NullContext()):
        if not isinstance(initial_state, State):
            raise TypeError(f"Initial state must be an instance of `State`: {type(initial_state) = }")

        if not isinstance(context, Context):
            raise TypeError(f"Context must be an instance of `Context`: {type(context) = }")
        
        if not isinstance(transition_table, StateTransitionTable):
            raise TypeError(f"Transition table must be an instance of "
                            f"`StateTransitionTable`: {type(transition_table) = }")

        self.__context = context
        self.__state: State = initial_state
        self.__transition_table = transition_table
        
    @property
    def state(self) -> State:
        return self.__state

    @property
    def context(self) -> Context:
        return self.__context

    def set_state(self, new_state: State):
        if not isinstance(new_state, State):
            raise TypeError(f"New state must be an instance of `State`: {type(new_state) = }")
        
        old_state = self.state
        
        old_state.before_exit()
        new_state.before_enter()
            
        self.__state = new_state
        self.context.state = new_state
        
        old_state.after_exit()
        new_state.after_enter()
        
    @property
    def transition_table(self) -> StateTransitionTable:
        return self.__transition_table
    
    @property
    def stt(self) -> StateTransitionTable:
        return self.__transition_table
    
    @property
    def is_in_final_state(self) -> bool:
        return self.state_type in self.transition_table.final_states
    
    @property
    def state_type(self) -> Type[State]:
        return type(self.state)

    def next_state(self, event: EventEnum, *args, **kwargs):
        new_state = self.transition_table.handle(event, type(self.state))
        if new_state is not None:
            self.set_state(new_state(*args, **kwargs))
