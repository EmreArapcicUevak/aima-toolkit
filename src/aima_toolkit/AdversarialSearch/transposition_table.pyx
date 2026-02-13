from libc.stdlib cimport malloc, free
from libc.string cimport memset

# 1. Define the entry as a C struct (16 bytes typically)
cdef struct TTEntry:
    unsigned long long key  # The full Zobrist hash (to verify identity)
    float score               # The evaluation score
    int depth               # How deep we searched
    int flags               # Exact, Lowerbound, or Upperbound
    int best_move           # The best move found (encoded as int)

cdef class TranspositionTable:
  cdef TTEntry * table
  cdef unsigned long long size

  def __cinit__(self, size_in_mb):
    # Calculate number of entries that fit in size_in_mb
    cdef size_t entry_size = sizeof(TTEntry)
    self.size = (size_in_mb * 1024 * 1024) // entry_size

    # Allocate raw C memory (fast, no Python GC)
    self.table = <TTEntry *> malloc( self.size * entry_size )

    # Initialize with zeros
    memset( self.table, 0, self.size * entry_size )

  def __dealloc__(self):
    # Manual cleanup is required for malloc
    if self.table:
      free( self.table )

  # Fast C-only method to store data
  cdef void store(self, unsigned long long key, int depth, int score, int flag, int move):
    cdef unsigned long long index = key % self.size
    cdef TTEntry * entry = &self.table[ index ]

    # REPLACEMENT STRATEGY:
    # Only overwrite if the new search is deeper or the slot is empty (or collision logic)
    if entry.key == 0 or depth >= entry.depth:
      entry.key = key
      entry.score = score
      entry.depth = depth
      entry.flags = flag
      entry.best_move = move

  # Fast C-only method to retrieve data
  cdef TTEntry * probe(self, unsigned long long key):
    cdef unsigned long long index = key % self.size
    cdef TTEntry * entry = &self.table[ index ]

    if entry.key == key:
      return entry
    return NULL