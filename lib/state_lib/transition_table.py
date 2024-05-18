from typing import Type, Tuple, Iterable, Dict, List, Union

from .state import State, FinalState, InitialState
from .helper import is_of_class_type
from .errors import EventAlreadyExists, IncorrectState, EventNotFound
from . import EventEnum


class Transition:
    def __init__(self, origin: Type[State], target: Type[State]):
        if is_of_class_type(origin, FinalState):
            raise IncorrectState(f"Origin cannot be `{origin.__name__}` because it is a final state")

        if is_of_class_type(target, InitialState):
            raise IncorrectState(f"Target cannot be `{origin.__name__}` because it is an initial state")

        self.__origin: Type[State] = origin
        self.__target: Type[State] = target

    @property
    def origin(self) -> Type[State]:
        return self.__origin

    @property
    def target(self) -> Type[State]:
        return self.__target

    def __repr__(self) -> str:
        return f"Transition({self.__origin.__qualname__}, {self.__target.__qualname__})"


class StateTransitionTable:
    def __init__(self, table: Union[Dict[EventEnum, Tuple], None] = None):
        self.__transition_table: dict = {}

        if table is None:
            return

        if not isinstance(table, dict):
            raise TypeError(f"Table must be a dictionary: {type(table) = }")

        for event, transitions in table.items():
            if not isinstance(transitions, tuple):
                raise TypeError(f"Transitions must be a tuple: {type(transitions) = }")

            formatted_transitions = self.__formate_transitions(transitions)

            self.add_event(event)
            for pair in formatted_transitions:
                self.add_transition(event, *pair)

    @staticmethod
    def __formate_transitions(transitions: Tuple) -> List:
        formatted = []

        if not isinstance(transitions, tuple):
            raise TypeError(f"Transitions must be a tuple: {type(transitions) = }")

        if all((isinstance(e, Transition) for e in transitions)):
            for transition in transitions:
                formatted.append((transition.origin, transition.target))

        elif all((isinstance(e, tuple) for e in transitions)):
            for transition in transitions:
                if len(transition) != 2:
                    raise ValueError(f"Transition must be a tuple of 2 elements: {transition = }")

                formatted.append(transition)

        elif len(transitions) == 2:
            if isinstance(transitions[0], tuple):
                for state in transitions[0]:
                    formatted.append((state, transitions[1]))

            else:
                formatted.append((*transitions,))

        else:
            raise ValueError(f"Unknown content: {transitions = }")

        return formatted

    @staticmethod
    def __validate(event: Union[EventEnum, None] = None, states: Iterable[Type[State]] = tuple()):
        if event and not isinstance(event, EventEnum):
            raise TypeError(f"Event must be a member of `EventNum` subclass: {type(event) = }")

        for state in filter(lambda s: not is_of_class_type(s, State), states):
            raise TypeError(f"Not a `State` subtype: {type(state) = }")

    def add_transition(self, event: EventEnum, origin: Type[State], target: Type[State]):
        self.__validate(event, (origin, target))

        if event not in self.events:
            self.add_event(event)

        self.__transition_table[event] = self.__transition_table[event] + (Transition(origin, target),)

    def remove_by_origin(self, event: EventEnum, origin: Type[State]):
        self.__validate(event, (origin,))

        if event not in self.events:
            raise EventNotFound(event)

        self.__transition_table[event] = tuple(filter(lambda t: t.origin != origin, self.__transition_table[event]))

    def remove_by_target(self, event: EventEnum, target: Type[State]):
        self.__validate(event, (target,))

        if event not in self.events:
            raise EventNotFound(event)

        self.__transition_table[event] = tuple(filter(lambda t: t.target != target, self.__transition_table[event]))

    def remove_event(self, event: EventEnum):
        self.__validate(event, tuple())

        if event not in self.events:
            raise EventNotFound(event)

        del self.__transition_table[event]

    def add_event(self, event: EventEnum):
        self.__validate(event, tuple())

        if event in self.events:
            raise EventAlreadyExists(event)

        self.__transition_table[event] = ()

    @property
    def events(self) -> set:
        return set(self.__transition_table.keys())

    @property
    def origin_states(self) -> set:
        states = [transition.origin
                  for record in self.__transition_table.values()
                  for transition in record
                  ]

        return set(states)

    @property
    def target_states(self) -> set:
        states = [transition.target
                  for record in self.__transition_table.values()
                  for transition in record
                  ]

        return set(states)

    @property
    def known_states(self) -> set:
        return self.origin_states.union(self.target_states)

    @property
    def final_states(self) -> set:
        return self.known_states.difference(self.origin_states)

    @property
    def unreachable_states(self) -> set:
        return self.known_states.difference(self.target_states)

    def handle(self, event: EventEnum, current_state: Type[State]) -> Union[Type[State], None]:
        self.__validate(event, (current_state,))

        if event not in self.events:
            raise EventNotFound(event)

        next_state = next(filter(lambda t: t.origin == current_state, self.__transition_table[event]), None)

        return next_state and next_state.target

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.__transition_table})"
