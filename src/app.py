from io import BytesIO
from pathlib import Path
from subprocess import PIPE, Popen

import streamlit as st
from PIL import Image

# Confit
st.set_page_config(page_title="放大", page_icon=":bar_chart:", layout="wide")


# Title
st.sidebar.title(":sunglasses:*二次元图片放大*")

# slider 范围2-4
s = st.sidebar.slider("放大倍数", 2, 4, 2, 1)
# 噪点 范围 -1 0 1 2 3
n = st.sidebar.slider("噪点", -1, 3, -1, 1)
# 是否开启TTA模式
tta = st.sidebar.checkbox("TTA模式")
# 输出格式 默认png
format_ = st.sidebar.selectbox("输出格式", ["png", "jpg", "webp"])
# 放大按钮
s_btn = st.sidebar.button("放大")

TEMP_DIR = Path(__file__).parent.parent / "temp"
OUTPUT_DIR = Path(__file__).parent.parent / "result"
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
REALCUGAN_PATH = (
    Path(__file__).parent.parent / "realCUGAN-ncnn-vulkan" / "realcugan-ncnn-vulkan.exe"
)


def enlarge(
    img: str, noise: int, scale: int, tta_enable: bool, format: str
) -> BytesIO | None:
    """利用Realcugan-ncnn-vulkan放大图片

    Args:
        img (str): 图片路径
        scale (int): 放大倍数

    Returns:
        bytes: 放大后的图片
    """
    # 生成命令
    out = OUTPUT_DIR / f"{Path(img).stem}_{scale}x.{format}"
    cmd = (
        f"{REALCUGAN_PATH} -i {img} -o {out} -n {noise} -s {scale} "
        f"{'-x' if tta_enable else ''} -f {format}"
    )
    print(cmd)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    # 等待执行完成
    p.wait()
    # 读取输出
    if out.exists():
        return BytesIO(out.read_bytes())
    # 弹出警告
    st.warning("放大失败")


uploaded_file = st.file_uploader(
    "上传图片", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

# 按钮，点击放大
if s_btn:
    # 循环读取图片
    assert uploaded_file
    with st.spinner("正在放大..."):
        for file in uploaded_file:
            # 读取图片
            img = Image.open(file)
            # 保存图片
            file = TEMP_DIR / file.name
            img.save(file)
            # 左右显示图片，左原图，右放大后
            c1, c2 = st.columns(2)
            c1.image(img, caption="原图", use_column_width=True)
            assert format_
            if result := enlarge(file, n, s, tta, format_):
                out_img = Image.open(result)
                c2.image(result, caption="放大后", use_column_width=True)
