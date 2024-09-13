# -*- coding: utf-8 -*-
# version: python 3.5
"""mdict_query

"""
from typing import Any

from.readmdict import MDX, MDD
from struct import pack, unpack
from io import BytesIO
import re
import os
import sqlite3
import json

# zlib compression is used for engine version >=2.0
import zlib

# LZO compression is used for engine version < 2.0
# from mdict_query import lzo
import lzo

class IndexBuilder:
    def __init__(self, fname, encoding="", passcode=None, force_rebuild=False, enable_history=False, sql_index=True,
                 check=False):
        self._mdx_file = fname
        self._mdd_file = ""
        self._encoding = ""
        self._stylesheet = {}
        self._title = ''
        self._description = ''
        self._sql_index = sql_index
        self._check = check
        _filename, _file_extension = os.path.splitext(fname)
        assert (_file_extension == '.mdx')
        assert (os.path.isfile(fname))
        self._mdx_db = _filename + ".mdx.db"
        if force_rebuild or not os.path.isfile(self._mdx_db):
            self._make_mdx_index(self._mdx_db)
        else:
            self._load_meta_data()
        if os.path.isfile(_filename + ".mdd"):
            self._mdd_file = _filename + ".mdd"
            self._mdd_db = _filename + ".mdd.db"
            if force_rebuild or not os.path.isfile(self._mdd_db):
                self._make_mdd_index(self._mdd_db)

    def _load_meta_data(self):
        with sqlite3.connect(self._mdx_db) as conn:
            cursor = conn.execute("SELECT * FROM META")
            for cc in cursor:
                if cc[0] == "encoding":
                    self._encoding = cc[1]
                elif cc[0] == "stylesheet":
                    self._stylesheet = json.loads(cc[1])
                elif cc[0] == "title":
                    self._title = cc[1]
                elif cc[0] == "description":
                    self._description = cc[1]

    def _replace_stylesheet(self, txt):
        # substitute stylesheet definition
        txt_list = re.split(r'`\d+`', txt)
        txt_tag = re.findall(r'`\d+`', txt)
        txt_styled = txt_list[0]
        for j, p in enumerate(txt_list[1:]):
            style = self._stylesheet[txt_tag[j][1:-1]]
            if p and p[-1] == '\n':
                txt_styled = txt_styled + style[0] + p.rstrip() + style[1] + '\r\n'
            else:
                txt_styled = txt_styled + style[0] + p + style[1]
        return txt_styled

    def _make_db_index(self, db_name, reader: MDX | MDD):
        if os.path.exists(db_name):
            os.remove(db_name)
        returned_index = reader.get_index(check_block=self._check)
        meta = None
        index_list = returned_index['index_dict_list']
        if isinstance(reader, MDX):
            meta = returned_index['meta']
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            ''' CREATE TABLE MDX_INDEX
               (key_text text not null,
                file_pos integer,
                compressed_size integer,
                decompressed_size integer,
                record_block_type integer,
                record_start integer,
                record_end integer,
                offset integer
                )'''
        )

        tuple_list = [
            (item['key_text'],
             item['file_pos'],
             item['compressed_size'],
             item['decompressed_size'],
             item['record_block_type'],
             item['record_start'],
             item['record_end'],
             item['offset']
             )
            for item in index_list
        ]
        c.executemany('INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?,?)',
                      tuple_list)
        if self._sql_index:
            c.execute(
                '''
                CREATE INDEX key_index ON MDX_INDEX (key_text)
                '''
            )

        # build the metadata table for mdx
        if meta is not None:
            c.execute(
                '''CREATE TABLE META
                   (key text,
                    value text
                    )''')

            c.executemany(
                'INSERT INTO META VALUES (?,?)',
                [('encoding', meta['encoding']),
                 ('stylesheet', meta['stylesheet']),
                 ('title', meta['title']),
                 ('description', meta['description']),
                 ]
            )
            # set class member
            self._encoding = meta['encoding']
            self._stylesheet = json.loads(meta['stylesheet'])
            self._title = meta['title']
            self._description = meta['description']

        conn.commit()
        conn.close()

    def _make_mdx_index(self, db_name: str) -> None:
        self._mdx_db = db_name
        if os.path.exists(db_name):
            os.remove(db_name)
        mdx = MDX(self._mdx_file)
        self._make_db_index(db_name, mdx)

    def _make_mdd_index(self, db_name):
        if os.path.exists(db_name):
            os.remove(db_name)
        mdd = MDD(self._mdd_file)
        self._make_db_index(db_name, mdd)

    def _get_by_index(self, fmdx, index, is_mdx=True):
        fmdx.seek(index['file_pos'])
        record_block_compressed = fmdx.read(index['compressed_size'])
        record_block_type = record_block_compressed[:4]
        record_block_type = index['record_block_type']
        decompressed_size = index['decompressed_size']
        if record_block_type == 0:
            _record_block = record_block_compressed[8:]
        elif record_block_type == 1:
            if lzo is None:
                print("LZO compression is not supported")
            header = b'\xf0' + pack('>I', index['decompressed_size'])
            _record_block = lzo.decompress(record_block_compressed[8:], initSize=decompressed_size,
                                           blockSize=1308672)
        elif record_block_type == 2:
            _record_block = zlib.decompress(record_block_compressed[8:])
        data = _record_block[index['record_start'] - index['offset']:index['record_end'] - index['offset']]
        if is_mdx:
            data = data.decode(self._encoding, errors='ignore').strip(u'\x00').encode('utf-8')
            if self._stylesheet:
                data = self._replace_stylesheet(data)
            data = data.decode('utf-8')
        return data

    def get_mdx_by_index(self, fmdx, index):
        return self._get_by_index(fmdx, index, is_mdx=True)

    def get_mdd_by_index(self, fmdx, index):
        return self._get_by_index(fmdx, index, is_mdx=False)

    def _db_lookup(self, keyword: str, file_path: str, db_path: str, is_mdx=True) -> list[str]:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(f'SELECT * FROM MDX_INDEX WHERE key_text="{keyword}"')
            lookup_result_list = []
            with open(file_path, 'rb') as _file:
                for result in cursor:
                    index = {}
                    index['file_pos'] = result[1]
                    index['compressed_size'] = result[2]
                    index['decompressed_size'] = result[3]
                    index['record_block_type'] = result[4]
                    index['record_start'] = result[5]
                    index['record_end'] = result[6]
                    index['offset'] = result[7]
                    lookup_result_list.append(self._get_by_index(_file, index, is_mdx))
            return lookup_result_list

    def mdx_lookup(self, keyword: str) -> list[str]:
        return self._db_lookup(keyword, self._mdx_file, self._mdx_db, True)

    def mdd_lookup(self, keyword):
        return self._db_lookup(keyword, self._mdd_file, self._mdd_db, False)

    def _get_keys(self, db_name, query=''):
        if not db_name:
            return []
        conn = sqlite3.connect(db_name)
        if query:
            if '*' in query:
                query = query.replace('*', '%')
            else:
                query = query + '%'
            cursor = conn.execute(f'SELECT key_text FROM MDX_INDEX WHERE key_text LIKE "{query}"')
        else:
            cursor = conn.execute('SELECT key_text FROM MDX_INDEX')
        keys = [item[0] for item in cursor]
        conn.close()
        return keys

    def get_mdd_keys(self, query=''):
        return self._get_keys(self._mdd_db, query)

    def get_mdx_keys(self, query=''):
        return self._get_keys(self._mdx_db, query)
