import json
import re
import gradio as gr
import LangSegment

# 如何安装？ How to install
# pip3 install LangSegment

# =================================================================
# 这是本项目的webui，运行脚本后，它将会打开浏览器网页，即可体验。
# This is the webui of this project. After running the script, it will open the browser web page and you can experience it.
# =================================================================

# gradio
print("gradio:", gr.__version__)

# 显示版本，display version
version = LangSegment.__version__
print("LangSegment:", version , LangSegment.__develop__)

# --------------------------------
# color label table
langdic = {
    "zh":["Chinese"  , "#F1F1F1"   ], # zh = 中文：  Chinese
    "en":["English"  , "green"     ], # en = 英文：  English
    "ja":["Japanese" , "yellow"    ], # ja = 日文：  Japanese
    "ko":["Korean"   , "blue"      ], # ko = 韩语：  Korean
    "fr":["French"   , "#ddc3ff"   ], # fr = 法语：  French
    "vi":["French"   , "#44c2ec"   ], # vi = 越南语：Vietnamese
    "ru":["Russian"  , "#CCCC99"   ], # vi = 俄语：  Russian
    "th":["Thai"     , "#FFCC00"   ], # th = 泰语：  Thai
    "no":["None"     , "red"       ], # no = 未定义：None
}

# --------------------------------
# Chinese translation，Can comment
langdic["zh"][0] = "中文(zh)"
langdic["en"][0] = "英文(en)"
langdic["ja"][0] = "日文(ja)"
langdic["ko"][0] = "韩文(ko)"
langdic["fr"][0] = "法语(fr)"
langdic["vi"][0] = "越南语(vi)"
langdic["ru"][0] = "俄语(ru)"
langdic["th"][0] = "泰语(th)"
langdic["no"][0] = "其它"


# 系统默认过滤器。System default filter。(ISO 639-1 codes given)
# ----------------------------------------------------------------------------------------------------------------------------------
# "zh"中文=Chinese ,"en"英语=English ,"ja"日语=Japanese ,"ko"韩语=Korean ,"fr"法语=French ,"vi"越南语=Vietnamese , "ru"俄语=Russian
# "th"泰语=Thai
# ----------------------------------------------------------------------------------------------------------------------------------

# 设置语言过滤器：默认为/中英日韩，(支持"fr"法语=French, "vi"越南语=Vietnamese, "ru"俄语=Russian, "th"泰语=Thai)
# Set language filters
ALL_LANGUAGE = ["fr", "vi" , "ja", "zh", "ko", "en" , "ru" , "th"]
LangSegment.setfilters(ALL_LANGUAGE[:])


# --------------------------------


# 自定义过滤器，方便在Dropdown使用中文展示，过滤器自带优先级功能。比如 ja-zh 其中 ja 日文优先。
# 以下是部份示例，可以随意拱配。
filter_list = [
    "中文zh/日文ja/英文en/韩文ko/法语fr/越南语vi/俄语ru/泰语th(ALL)", # ALL_LANGUAGE
    "中文-日文-英文-韩文",
    "中文",
    "英文",
    "日文",
    "韩文",
    "法语",
    "越南语",
    "俄语",
    "泰语",
    "中文-英文",
    "中文-法语",
    "中文-日文",
    "中文-越南语",
    "中文-俄语",
    "中文-泰语",
    "日文-中文-泰语",
    "法语-日文-英文-俄语",
    "越南语-日文-韩文-泰语",
]

# 中文界面显示翻译映射。filter_list 中的字符，必须和下面的表匹配。
dict_language={
    "中文zh/日文ja/英文en/韩文ko/法语fr/越南语vi/俄语ru/泰语th(ALL)":"all", # ALL_LANGUAGE
    "中文":"zh",
    "英文":"en",
    "日文":"ja",
    "韩文":"ko",
    "法语":"fr",
    "越南语":"vi",
    "俄语":"ru",
    "泰语":"th",
}

# --------------------------------

def getLanglabel(lang):
    lang = lang if lang in langdic else "no"
    fullKey = langdic[lang][0]
    return fullKey

color_map = {}
for lang in langdic:
    data = langdic[lang]
    fullKey , color = data[0] , data[1]
    color_map[fullKey] = color
# print(color_map)

# 处理：
def parse_language(input_text):
    noneKey = getLanglabel("no")
    output = ""
    codes = []
    codes.append(("\n",noneKey))
    # 当前的过滤器
    print(LangSegment.getfilters())
    # （1）处理分词 processing participle
    langlist = LangSegment.getTexts(input_text)
    for data in langlist:
        output += f'{str(data)}\n'
        lang = data['lang']
        text = data['text']
        text = re.sub(r'\n+','\n',text)
        codes.append((text , getLanglabel(lang)))
    codes.append(("\n\n",noneKey))
    # （2）统计分词 Statistical participle
    label_text = "没有结果显示"
    langCounts = LangSegment.getCounts()
    if len(langCounts) > 0:
        lang , count = langCounts[0] 
        filters = LangSegment.getfilters()
        label_text = f"您输入的主要语言为：【{getLanglabel(lang)}】。\n参考依据：{str(langCounts)}。\n过滤设置：LangSegment.setfilters({filters})"
    return output , codes , label_text

# 过滤：
def lang_selected(option:str):
    # 列表中文映射
    filterValues = option
    for key in dict_language:
        filterValues = filterValues.replace(key,dict_language[key])
    # 设置过滤器值
    print(f"你选择了语言过滤器： {option} ==> {filterValues} ")
    # all = 代表保留所有语言，这里限定：中/英/日/韩/法，定义为：ALL_LANGUAGE
    filterValues = ALL_LANGUAGE if filterValues == "all" else [filterValues]
    LangSegment.setfilters(filterValues)
    pass


# 推荐使用 gradio==3.50.2
def onPageInit():
    filters_value = filter_list[0]
    print(f"默认过滤保留语言：{filters_value}")
    # 兼容 gradio 的版本
    if hasattr(gr.Dropdown, 'update'):
        # gradio 3.x , 3.50.2
        print("loaded gradio 3.x")
        return gr.Dropdown.update(value=filters_value)
    else:
        # gradio 4.x
        print("loaded gradio 4.x")
        return gr.Dropdown(value=filters_value, interactive=True)


# Translated from Google：
#LangSegment Text-to-Speech TTS Multilingual Word Segmentation\ n\
# < b > Introduction: It is a powerful multi-lingual (97 languages) hybrid text automatic word segmentation tool. [China, Japan, UK and Korea: Tested] </b > < br >\
# Main use: It is well-suited for various TTS Text To Speech projects (e.g. vits), front-end inference for multilingual mixed text, and pre-processing back-end training. LICENSE is detailed in the root directory < br >\
# < b > Connect it to your vits project and install it on python: pip3 install LangSegment\ t (CN domestic image): pip3 install LangSegment -i https://pypi.mirrors.ustc.edu.cn/simple </b > < br >\
# If you encounter any problems, please go to github to provide feedback and make it easier to use: https://github.com/juntaosun/LangSegment < br >\

# Translated from Google：
#  Instructions for use: The default is automatic word segmentation. You can also manually add language tags to get more accurate word segmentation results: < br >
#     (1) Automatic word segmentation: If you encounter Chinese and Japanese, the recognition error is due to the overlap of Chinese characters, you can type a space to assist word segmentation (automatic context word segmentation). < br >
#     (2) Manual word segmentation: language tags\ < ja\ > Japanese </ja\ >,\ < ko \>언니\</ ko\ >,\ < zh\ > Hello\ </zh\ >,\ < en\ > Hello World\ </en\ > to assist word segmentation. < br >
#          Other language tags such as：\<fr\>Français\</fr\>、\<vi\>Tiếng Việt\</vi\>、
#     (3) English capital abbreviations: such as USA, ChatGPT. The result is: U S A, ChatG P T. Text To Speech is often separated by spaces to allow letters to be pronounced alone.

lang_desc = """
    使用说明：默认为自动分词，您也可以手动添加语言标签，来获得更精准的分词结果：<br>
    （1）自动分词：若遇到中文与日语，因汉字重叠相连而识别错误，您可打上句号。来辅助分词（上下文分词）。<br>
    （2）手动分词：语言标签 \<ja\>日本語\</ja\>、\<ko\>언니\</ko\>、\<zh\>你好\</zh\>、\<en\>Hello World\</en\> 来辅助分词。 <br>
    （3）英文大写缩略词：如USA、ChatGPT。结果为：U S A、ChatG P T。语音合成常用空格分隔，让字母单独发音。
"""

# 默认示例混合文本：中/英/日/韩/法/越/俄/泰
example_text = """
我喜欢在雨天里听音乐。
I enjoy listening to music on rainy days.
雨の日に音楽を聴くのが好きです。
비 오는 날에 음악을 듣는 것을 즐깁니다。
J'aime écouter de la musique les jours de pluie.
Tôi thích nghe nhạc vào những ngày mưa.
Мне нравится слушать музыку в дождливую погоду.
ฉันชอบฟังเพลงในวันที่ฝนตก
"""


gr_css = """
.lang_button {
    height: 80px;
}
.codes_text {
    min-height: 450px;
}
"""



with gr.Blocks(title="LangSegment WebUI" , css=gr_css) as app:
    gr.Markdown(
        value=f"# LangSegment 文本转语音专用，TTS混合语种分词 [v{LangSegment.__version__}]\n \
        <b>简介：它是一个强大的多语言（97种语言）的混合文本自动分词工具。[中日英韩：已测试]</b><br> \
        主要用途：它非常适合各种 TTS 语音合成项目（例如：vits），多语种混合文本的前端推理，和预处理后端训练。LICENSE详见根目录<br> \
        <b>将它接入您的vits项目，在python上安装：``` pip3 install LangSegment>={version} -i  https://pypi.org/simple ```</b><br> \
        若遇到问题，欢迎前往github提供反馈，一起让它变得更易用： https://github.com/juntaosun/LangSegment <br> \
        "
    )
    with gr.Group(): # gr.Dropdown.update(choices=filter_list)["choices"]
        with gr.Row():
            with gr.Column():
                input_text  = gr.TextArea(label=f"【分词输入】：多语种混合文本内容。目前仅专注（中文Chinese、日文Japanese、英文English、韩文Korean）", value=f"{example_text}",lines=12)
                # [Word input]: Multilingual mixed text content. Currently specially supported (Chinese, Japanese, English, Korean)
                gr.Markdown(value=f"{lang_desc}")
                lang_filters = gr.Dropdown(choices=filter_list, label='【语言过滤】：设置需要保留的语言，过滤其它语言。(API：LangSegment.setfilters)')
                # TTS multilingual mixed text, click for word segmentation
                lang_button = gr.Button("✨TTS多语言混合文本 , 点击进行分词处理", variant="primary",elem_classes=["lang_button"])
            with gr.Column():
                with gr.Tabs():
                    # A: Toggle the result to highlight
                    with gr.TabItem("A：切换高亮结果显示"):
                        with gr.Column():
                            # [Word segmentation result]: Multi-language mixed highlighting: different languages correspond to different colors.
                            codes_text = gr.HighlightedText(
                                label="【分词结果】：多国语言混合高亮显示：不同语言对应不同的颜色。", 
                                scale=2,
                                show_label=True,
                                combine_adjacent=True,
                                show_legend=True,
                                color_map=color_map,
                                elem_classes=["codes_text"],
                            )
                    # B: Toggle the result code display
                    with gr.TabItem("B：切换代码结果显示"):
                        with gr.Column():
                            # [Word segmentation result]: Multiple languages have been separated (Chinese, Japanese, English, Korean), just enter TTS Text To Speech directly.
                            output_text = gr.TextArea(label="【分词结果】：多国语言已经分离完成（中zh、日ja、英en、韩ko），直接输入TTS语音合成处理即可。", value="",lines=19)
                # [Word segmentation statistics]: According to the processing results, predict the main language you entered.
                label_text = gr.Text(label="【分词统计】：根据处理结果，推测您输入的主要语言。", value="")
            
        
        lang_button.click(
            parse_language,
            [input_text],
            [output_text , codes_text ,label_text],
        )
        
        lang_filters.change(
            lang_selected,
            [lang_filters]
        )
        
        app.load(
            onPageInit,
            [],
            [lang_filters],
            )


# 注意 gradio 3.x 和 gradio 4.x 启动参数有差异。
if int(gr.__version__.split(".")[0]) >= 4:
    app = app.queue() # gradio 4.x
else:
    app = app.queue(concurrency_count=511, max_size=1022) # gradio 3.x / 3.50.2
  
    
# 推荐使用 gradio==3.50.2
app.launch(
        server_name="0.0.0.0",
        inbrowser=True,
        share=False,
        server_port=6066,
        quiet=True,
    )