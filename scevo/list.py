import itertools

class List:
  @staticmethod
  def chunk(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

  @staticmethod
  def flatten(list_of_lists):
    return list(itertools.chain.from_iterable(list_of_lists))
