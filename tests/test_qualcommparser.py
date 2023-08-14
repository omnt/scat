#!/usr/bin/env python3

import unittest
import binascii
import datetime
from collections import namedtuple

from scat.parsers.qualcomm.qualcommparser import QualcommParser

class TestQualcommParser(unittest.TestCase):
    parser = QualcommParser()
    log_header = namedtuple('QcDiagLogHeader', 'cmd_code reserved length1 length2 log_id timestamp')

    def test_parse_diag_version(self):
        payload = binascii.unhexlify('004e6f76202032203230323132323a31333a31324f6374203132203230323130323a30303a303073647835352e63702a09ff64003000cf')
        result = self.parser.parse_diag_version(payload)
        expected = {'stdout': 'Compile: Nov  2 2021/22:13:12, Release: Oct 12 2021/02:00:00, Chipset: sdx55.cp'}
        self.assertDictEqual(result, expected)

    def test_parse_ext_build_id(self):
        payload = binascii.unhexlify('7c010000f20c00004e010000524d35303051474c41425231314130364d34470000')
        result = self.parser.parse_diag_ext_build_id(payload)
        expected = {'stdout': 'Build ID: RM500QGLABR11A06M4G'}
        self.assertDictEqual(result, expected)

    def test_parse_log_config(self):
        payload = binascii.unhexlify('73000000010000000000000000000000ff0f00000000000000000000f70f0000f70f00001c0000005e0b00000000000016080000920300000902000000000000070200000000000000000000')
        result = self.parser.parse_diag_log_config(payload)
        expected = {'stdout': 'Log Config: Retrieve ID ranges: 1: 4095, 4: 4087, 5: 4087, 6: 28, 7: 2910, 9: 2070, 10: 914, 11: 521, 13: 519, '}
        self.assertDictEqual(result, expected)

    def test_parse_ext_msg_config(self):
        payload = binascii.unhexlify('7d0101001a00000000008600f401fa01e803b004d007d807b80bc60ba00faa0f9411e811f81108128813ac137c158d157017c11764197919581b5b1bbc1bc71b201c211c401f401f34215421282330231c253125d827e2270b280f283c283c286e288928a028b0280429092900c063c0')
        result = self.parser.parse_diag_ext_msg_config(payload)
        expected = {'stdout': 'Extended message range: 0-134, 500-506, 1000-1200, 2000-2008, 3000-3014, 4000-4010, 4500-4584, 4600-4616, 5000-5036, 5500-5517, 6000-6081, 6500-6521, 7000-7003, 7100-7111, 7200-7201, 8000-8000, 8500-8532, 9000-9008, 9500-9521, 10200-10210, 10251-10255, 10300-10300, 10350-10377, 10400-10416, 10500-10505, 49152-49251, '}
        self.assertEqual(result['stdout'], expected['stdout'])

    def test_parse_diag_ext_msg(self):
        # "Sample record, config app to start/stop = 1, carrier=0, rec_buf=0, rxagc_mode =1"
        payload = binascii.unhexlify('7900000000b07564160000007c00fc110400000053616d706c65207265636f72642c20636f6e6669672061707020746f2073746172742f73746f70203d20312c20636172726965723d302c207265635f6275663d302c2072786167635f6d6f6465203d31006c74655f4c4c315f73616d706c655f7265636f72645f64617461626173652e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d5369a0005e916000000000000000000000000000000000000000000000000343630340000000000000000000000006c74655f4c4c315f73616d706c655f7265636f72645f64617461626173652e630000007c53616d706c65207265636f72642c20636f6e6669672061707020746f2073746172742f73746f70203d20312c20636172726965723d302c207265635f6275663d302c2072786167635f6d6f6465203d31')
        self.assertEqual(result['cp'][0], expected_cp)

        # HST DEBUG: received UMID %d
        payload = binascii.unhexlify('7900010000983c97160000004906252504000000060438044853542044454255473a20726563656976656420554d4944202564006c74655f6d6c315f6d67725f7461736b2e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d536aa0009b42e000000000000000000000000000000000000000000000000393530390000000000000000000000006c74655f6d6c315f6d67725f7461736b2e630000000000000000000000000000000006494853542044454255473a20726563656976656420554d4944203730373739393130')
        self.assertEqual(result['cp'][0], expected_cp)

        # ADM: DeviceCmdQ [%d] rcvd APR msg [opcode] = [0x%08x]
        payload = binascii.unhexlify('790002000000ae6900000000b403342104000000010000002703010041444d3a20446576696365436d6451205b25645d207263766420415052206d7367205b6f70636f64655d203d205b3078253038785d004175644465764d67722e63707000')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d52f91000c795c000000000000000000000000000000000000000000000000383530300000000000000000000000004175644465764d67722e63707000000000000000000000000000000000000000000003b441444d3a20446576696365436d6451205b315d207263766420415052206d7367205b6f70636f64655d203d205b307830303031303332375d')
        self.assertEqual(result['cp'][0], expected_cp)

        # "debug TxAGC GRFC:0x%X, SF type:%d"
        payload = binascii.unhexlify('790002000040926d160000000b070e001c0000000601000007000000646562756720547841474320475246433a307825582c20534620747970653a25640072666c6d5f6c74655f74786167632e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d5369d00049f340000000000000000000000000000000000000000000000003134000000000000000000000000000072666c6d5f6c74655f74786167632e63000000000000000000000000000000000000070b646562756720547841474320475246433a30783130362c20534620747970653a37')
        self.assertEqual(result['cp'][0], expected_cp)

        # "tune_pll- Target Tx tune requency:%lu, Band:%d"
        payload = binascii.unhexlify('790002000000906d16000000b60d0e000400000039e44e680300000074756e655f706c6c2d205461726765742054782074756e652072657175656e63793a256c752c2042616e643a256400777472323936355f7472785f6c74655f74785f636c6173732e63707000')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d5369d000493e000000000000000000000000000000000000000000000000031340000000000000000000000000000777472323936355f7472785f6c74655f74785f636c6173732e6370700000000000000db674756e655f706c6c2d205461726765742054782074756e652072657175656e63793a313735303030303639372c2042616e643a33')
        self.assertEqual(result['cp'][0], expected_cp)

        # "wtr2965 pwr vote(after): st=%d, last=%d, return=%d "
        payload = binascii.unhexlify('7900030000283b6516000000571c0e0004000000030000000100000001000000777472323936352070777220766f7465286166746572293a2073743d25642c206c6173743d25642c2072657475726e3d25642000777472323936355f636f6d6d6f6e2e63707000')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d5369a0009ac9000000000000000000000000000000000000000000000000031340000000000000000000000000000777472323936355f636f6d6d6f6e2e637070000000000000000000000000000000001c57777472323936352070777220766f7465286166746572293a2073743d332c206c6173743d312c2072657475726e3d3120')
        self.assertEqual(result['cp'][0], expected_cp)

        # "UIM_%d: Path length is 4, Current Path 0x%x 0x%x 0x%x"
        payload = binascii.unhexlify('790004000068426516000000a30315000400000001000000003f0000107f00003a5f000055494d5f25643a2050617468206c656e67746820697320342c2043757272656e7420506174682030782578203078257820307825780075696d7574696c2e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d5369a0009d04e0000000000000000000000000000000000000000000000003231000000000000000000000000000075696d7574696c2e630000000000000000000000000000000000000000000000000003a355494d5f313a2050617468206c656e67746820697320342c2043757272656e742050617468203078336630302030783766313020307835663361')
        self.assertEqual(result['cp'][0], expected_cp)

        # "[NETKIT] rssi=%d rsrp=%d ecio=%d rsrq=%d rscp=%d"
        payload = binascii.unhexlify('790005000004be5c16000000860a8813080000007d0000000000000005000000ffffffff83ffffff5b4e45544b49545d20727373693d256420727372703d2564206563696f3d256420727372713d256420727363703d25640064735f716d695f6e65746b69742e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d53697000e00150000000000000000000000000000000000000000000000003530303000000000000000000000000064735f716d695f6e65746b69742e63000000000000000000000000000000000000000a865b4e45544b49545d20727373693d31323520727372703d30206563696f3d3520727372713d2d3120727363703d2d313235')
        self.assertEqual(result['cp'][0], expected_cp)

        # "rsrp=%ld rsrq=%d,lac=%d tac=%d rac_or_mme_code=%d"
        payload = binascii.unhexlify('790005000098f86216000000740988130800000000000000ffffffffffff00000000000000000000727372703d256c6420727372713d25642c6c61633d2564207461633d2564207261635f6f725f6d6d655f636f64653d25640064735f716d695f6e65746b69742e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d53699000de6660000000000000000000000000000000000000000000000003530303000000000000000000000000064735f716d695f6e65746b69742e63000000000000000000000000000000000000000974727372703d3020727372713d2d312c6c61633d3635353335207461633d30207261635f6f725f6d6d655f636f64653d30')
        self.assertEqual(result['cp'][0], expected_cp)

        # "uarfcn_dl=%d,uarfcn_ul=%d earfcn_dl=%d earfcn_ul=%d band=%d ch=%d"
        payload = binascii.unhexlify('790006000094c58a160000006409881308000000ffff0000ffff000040060000ffffffff7a0000000000000075617266636e5f646c3d25642c75617266636e5f756c3d25642065617266636e5f646c3d25642065617266636e5f756c3d25642062616e643d25642063683d25640064735f716d695f6e65746b69742e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d536a60009e0070000000000000000000000000000000000000000000000003530303000000000000000000000000064735f716d695f6e65746b69742e6300000000000000000000000000000000000000096475617266636e5f646c3d36353533352c75617266636e5f756c3d36353533352065617266636e5f646c3d313630302065617266636e5f756c3d2d312062616e643d3132322063683d30')
        self.assertEqual(result['cp'][0], expected_cp)

        # "HIGH PRIO: op_id %d snd %d freq_avail %d start %u end %u freq# %d freq %d"
        payload = binascii.unhexlify('790007000058b66d16000000421f2525020000020000000000000000000000000000000000000000000000000000000048494748205052494f3a206f705f696420256420736e6420256420667265715f617661696c20256420737461727420257520656e642025752066726571232025642066726571202564006c74655f6d6c315f636f65782e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d5369d00054f92000000000000000000000000000000000000000000000000393530390000000000000000000000006c74655f6d6c315f636f65782e6300000000000000000000000000000000000000001f4248494748205052494f3a206f705f6964203020736e64203020667265715f617661696c2030207374617274203020656e642030206672657123203020667265712030')
        self.assertEqual(result['cp'][0], expected_cp)

        # Sent Init Acq Req; earfcn %d freq_100KHz %d max_freq_offset %d  targeted_acq_flag %d target_cid %d max hf %d num_blocked_cells %d fscan mode: %d
        payload = binascii.unhexlify('7900080000a04065160000003f092525040000009509000027220000bc340000000000000000000004000000000000000000000053656e7420496e697420416371205265713b2065617266636e20256420667265715f3130304b487a202564206d61785f667265715f6f6666736574202564202074617267657465645f6163715f666c6167202564207461726765745f636964202564206d6178206866202564206e756d5f626c6f636b65645f63656c6c7320256420667363616e206d6f64653a202564006c74655f6d6c315f6d642e6300')
        result = self.parser.parse_diag_ext_msg(payload)
        expected_cp = binascii.unhexlify('0204100000000000000000000000000012d5369a0009c7e8000000000000000000000000000000000000000000000000393530390000000000000000000000006c74655f6d6c315f6d642e6300000000000000000000000000000000000000000000093f53656e7420496e697420416371205265713b2065617266636e203234353320667265715f3130304b487a2038373433206d61785f667265715f6f6666736574203133353030202074617267657465645f6163715f666c61672030207461726765745f6369642030206d61782068662034206e756d5f626c6f636b65645f63656c6c73203020667363616e206d6f64653a2030')
        self.assertEqual(result['cp'][0], expected_cp)

if __name__ == '__main__':
    unittest.main()
