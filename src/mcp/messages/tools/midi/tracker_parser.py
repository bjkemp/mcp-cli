"""
Tracker file parser for MIDI generation.

This module parses tracker file format strings and converts them to MIDI events.
"""
from typing import Dict, List, Tuple, Optional


# Note name to MIDI note number mapping
NOTE_MAP = {
    "C-": 0, "C#": 1, "D-": 2, "D#": 3, "E-": 4, "F-": 5,
    "F#": 6, "G-": 7, "G#": 8, "A-": 9, "A#": 10, "B-": 11
}


class TrackerEvent:
    """Represents a single event in a tracker pattern."""
    def __init__(
        self,
        row: int,
        note: Optional[int] = None,
        instrument: Optional[int] = None,
        volume: Optional[int] = None,
        effect: Optional[str] = None,
        effect_param: Optional[int] = None
    ):
        self.row = row
        self.note = note  # MIDI note number
        self.instrument = instrument
        self.volume = volume
        self.effect = effect
        self.effect_param = effect_param
    
    def __repr__(self):
        return (
            f"TrackerEvent(row={self.row}, note={self.note}, "
            f"instrument={self.instrument}, volume={self.volume}, "
            f"effect={self.effect}, effect_param={self.effect_param})"
        )


class TrackerPattern:
    """Represents a pattern in a tracker file."""
    def __init__(self, pattern_idx: int, num_rows: int = 64):
        self.pattern_idx = pattern_idx
        self.num_rows = num_rows
        self.channels: Dict[int, List[TrackerEvent]] = {}
    
    def add_event(self, channel: int, event: TrackerEvent):
        """Add an event to the specified channel."""
        if channel not in self.channels:
            self.channels[channel] = []
        self.channels[channel].append(event)
    
    def __repr__(self):
        return f"TrackerPattern(pattern_idx={self.pattern_idx}, channels={len(self.channels)})"


class TrackerSong:
    """Represents a complete tracker song."""
    def __init__(self, title: str = "Untitled", bpm: int = 120, speed: int = 6):
        self.title = title
        self.bpm = bpm
        self.speed = speed  # Ticks per row
        self.patterns: Dict[int, TrackerPattern] = {}
        self.sequence: List[int] = []  # Pattern play order
    
    def add_pattern(self, pattern: TrackerPattern):
        """Add a pattern to the song."""
        self.patterns[pattern.pattern_idx] = pattern
    
    def set_sequence(self, sequence: List[int]):
        """Set the pattern play sequence."""
        self.sequence = sequence
    
    def __repr__(self):
        return (
            f"TrackerSong(title='{self.title}', bpm={self.bpm}, "
            f"patterns={len(self.patterns)}, sequence_length={len(self.sequence)})"
        )


def parse_note_string(note_str: str) -> Optional[int]:
    """Parse a note string (e.g., 'C-4') into a MIDI note number."""
    if not note_str or note_str == "...":
        return None
    
    # Handle note cut/off special cases
    if note_str == "===":  # Note cut
        return -1
    
    if len(note_str) != 3:
        return None
    
    note_name = note_str[0:2]
    octave = int(note_str[2])
    
    if note_name not in NOTE_MAP:
        return None
    
    return NOTE_MAP[note_name] + (octave * 12)


def parse_tracker_string(tracker_str: str) -> TrackerSong:
    """Parse a tracker file string and return a TrackerSong object."""
    lines = tracker_str.strip().split("\n")
    song = TrackerSong()
    
    # Track current pattern being parsed
    current_pattern = None
    pattern_started = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Parse header commands
        if line.startswith("#"):
            parts = line[1:].strip().split(":", 1)
            if len(parts) == 2:
                cmd, value = parts[0].strip().upper(), parts[1].strip()
                
                if cmd == "TITLE":
                    song.title = value
                elif cmd == "BPM":
                    try:
                        song.bpm = int(value)
                    except ValueError:
                        pass
                elif cmd == "SPEED":
                    try:
                        song.speed = int(value)
                    except ValueError:
                        pass
                elif cmd == "SEQUENCE":
                    try:
                        song.sequence = [int(x.strip()) for x in value.split(",")]
                    except ValueError:
                        pass
            continue
        
        # Parse pattern start
        if line.startswith("PATTERN"):
            try:
                pattern_idx = int(line.split()[1])
                rows = 64  # Default
                
                # Check if rows are specified
                if "ROWS" in line:
                    rows_idx = line.find("ROWS")
                    rows_str = line[rows_idx:].split()[1]
                    rows = int(rows_str)
                
                current_pattern =