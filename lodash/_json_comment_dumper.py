import json5
from typing import Any


class DumpListWithComments(json5.dumper.DefaultDumper):
    def dump(self, node):
        if isinstance(node, list):
            return self.list_to_json(node)
        else:
            return super().dump(node)

    def list_to_json(self, the_list: list[Any]) -> Any:
        self.env.write('[', indent=0)
        if self.env.indent:
            self.env.indent_level += 1
            self.env.write('\n', indent=0)
        list_length = len(the_list)
        for index, item in enumerate(the_list, start=1):
            self.env.write(' /* index: ' + str(index - 1) + ' */ ')
            if self.env.indent:
                self.env.write('')
            self.dump(item)
            if index != list_length:
                if self.env.indent:
                    self.env.write(',', indent=0)
                else:
                    self.env.write(', ', indent=0)
            if self.env.indent:
                self.env.write('\n', indent=0)
        if self.env.indent:
            self.env.indent_level -= 1
        self.env.write(']')
