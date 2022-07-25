from printers.base_printer import BasePrinter


class ConsolePrinter(BasePrinter):

    def _print(self, msg, level):
        print(msg)
