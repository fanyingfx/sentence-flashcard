# -*- coding: utf-8 -*-
# version: python 3.5
"""
process mdx file query
"""
import re
from pathlib import Path

from bs4 import BeautifulSoup
from .index_builder import IndexBuilder

content_type_map = {
    "html": "text/html; charset=utf-8",
    "js": "application/x-javascript",
    "ico": "image/x-icon",
    "css": "text/css",
    "jpg": "image/jpeg",
    "png": "image/png",
    "bmp": "image/bmp",
    "gif": "image/gif",
    "mp3": "audio/mpeg",
    "mp4": "audio/mp4",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "eot": "font/opentype",
    "svg": "text/xml",
    "ttf": "application/x-font-ttf",
    "woff": "application/x-font-woff",
    "woff2": "application/font-woff2",
}


# from file_util import *


def process_audio(soup: BeautifulSoup):
    l = soup.find_all("a", {"class": ["sound", "aud-btn"]})
    for a in l:
        a.name = "span"
        a.attrs["onclick"] = (
            "function pl(el){if (el.nodeName=='AUDIO') el.play(); console.log(el)};function playAudio(e){"
            "e.childNodes.forEach(pl)};playAudio(this)"
        )
        href = a.get("href")
        sound_file = href.split("//")[-1]
        sound_type = sound_file.split(".")[-1]
        sound_type = f"audio/{sound_type}"
        audio = soup.new_tag("audio")
        audio.append(soup.new_tag("source", src=sound_file, type=f"{sound_type}"))
        a.append(audio)
        a.attrs.pop("href", None)
    return str(soup)


def get_definition_mdx(word, builder):
    """根据关键字得到MDX词典的解释"""
    # print("lookup word: ", word, word == word.strip())
    content = builder.mdx_lookup(word)
    # print('lookup content: ',content)
    if not content:
        content = "".encode("utf-8")
        return content
    pattern = re.compile(r"@@@LINK=(.*)")
    res = []
    for cnt in content:
        rst = pattern.match(cnt)
        if rst is not None:
            link = rst.group(1).strip()
            content = builder.mdx_lookup(link)
        str_content = ""
        if len(content) > 0:
            for c in content:
                str_content += c.replace("\r\n", "").replace("entry:/", "")
        s_html = BeautifulSoup(str_content, "html.parser")
        str_content = process_audio(s_html)

        res.append(str_content)

    output_html = "<br/>".join(res)
    return output_html.encode("utf-8")


def get_definition_mdd(word, builder: IndexBuilder):
    """根据关键字得到MDX词典的媒体"""
    word = word.replace("/", "\\")
    content = builder.mdd_lookup(word)
    if len(content) > 0:
        return content[0]
    return b""


# get_local_resource(resource_path)
# print(local_map.keys())


# print("resouce path : " + resource_path)
builder = None


class MDXDict:
    def __init__(self, mdx_file_path: Path, name=None,encoding:str='') -> None:
        self.builder = IndexBuilder(mdx_file_path.as_posix(),encoding=encoding)
        self.local_map = self.get_local_resource(mdx_file_path.parent)
        self.name = name

    @staticmethod
    def get_local_resource(resource_path: Path):
        local_map = {}
        for item in resource_path.iterdir():
            if item.suffix[1:] in content_type_map:
                with open(item, "rb") as f:
                    content = f.read()
                    local_map[item.name] = content

        return local_map

    def lookup(self, resource_name: str) -> bytes:
        file_extension = resource_name.split(".")[-1]
        if resource_name in self.local_map:
            res = self.local_map[resource_name]
        elif file_extension in content_type_map:
            res = get_definition_mdd(f"/{resource_name}", self.builder)
        else:
            res = get_definition_mdx(resource_name, self.builder)
        if res is None:
            res = b""
            print("none", resource_name)
        return res
