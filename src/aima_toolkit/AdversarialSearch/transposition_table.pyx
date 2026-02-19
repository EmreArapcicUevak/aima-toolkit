from tarfile import NUL

from docutils.nodes import entry
from libc.stdlib cimport malloc, free
from libc.string cimport memset
from typing import Any, Iterator


# 1. Define the entry as a C struct (16 bytes typically)
cdef struct TTEntry:
    long long key  # The full Zobrist hash (to verify identity)
    double score               # The evaluation score
    unsigned int depth               # How deep we searched
    int flags               # Exact, Lowerbound, or Upperbound
    int best_move           # The best move found (encoded as int)

cdef class TranspositionTable:
  cdef TTEntry * table
  cdef unsigned long long size

  def __cinit__(self, unsigned int size_in_mb):
    # Calculate number of entries that fit in size_in_mb
    cdef size_t entry_size = sizeof(TTEntry)
    self.size = (size_in_mb * 1024 * 1024) // entry_size

    if self.size == 0:
      self.table = NULL
      return

    # Allocate raw C memory (fast, no Python GC)
    self.table = <TTEntry *> malloc( self.size * entry_size )
    if not self.table:
      raise MemoryError( )

    # Initialize with zeros
    memset( self.table, 0, self.size * entry_size )

  def __dealloc__(self):
    # Manual cleanup is required for malloc
    if self.table:
      free( self.table )

  # Fast C-Python method to store data
  cpdef store(self, long long key, unsigned int depth, double score, int flag, int move):
    if self.size == 0:
      return

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
  cdef TTEntry* _probe(self, unsigned long long key) :
    if self.size == 0:
      return NULL

    cdef unsigned long long index = key % self.size
    cdef TTEntry * entry = &self.table[ index ]

    if entry.key == key:
      return entry
    return NULL

  def probe(self, long long key, player, actions : Iterator) -> tuple[dict[Any, float], Any] | None:
    cdef TTEntry* res = self._probe(key)
    cdef unsigned int i

    if res == NULL:
      return None

    move = next(actions)
    for i in range(res.best_move):
      move = next( actions )

    return {player : res.score}, move