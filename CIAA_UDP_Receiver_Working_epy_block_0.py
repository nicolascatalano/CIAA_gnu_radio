import numpy as np
import pmt
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self,
            name="to_selector_index",
            in_sig=[np.uint8],
            out_sig=None)

        self.message_port_register_out(pmt.intern("out"))
        self.last = None

    def work(self, input_items, output_items):
        data = input_items[0]
        v = int(data[-1])  # último valor (0/1)

        if self.last is None or v != self.last:
            msg = pmt.cons(pmt.PMT_NIL, pmt.from_long(v))
            self.message_port_pub(pmt.intern("out"), msg)
            self.last = v

        return len(data)
