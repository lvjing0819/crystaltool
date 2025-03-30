import os
import barcode
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

def generate_pdf(seller_sku, width_cm, length_cm, quantity):
    # 转换尺寸为毫米
    width_mm = width_cm * 10  # 页面宽度
    length_mm = length_cm * 10  # 页面高度

    # 创建条形码
    code128 = barcode.get_barcode_class('code128')
    barcode_obj = code128(seller_sku, writer=ImageWriter())

    # 将条形码保存为字节流
    barcode_io = BytesIO()
    barcode_obj.write(barcode_io)
    barcode_io.seek(0)

    # 设置文件保存路径
    pdf_directory = "/Volumes/Elements/code/小程序演示视频"
    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)  # 如果文件夹不存在，则创建

    # 设置 PDF 文件路径
    pdf_path = os.path.join(pdf_directory, f"{seller_sku}_barcode.pdf")

    # 创建 PDF 文件
    c = canvas.Canvas(pdf_path, pagesize=(width_mm ,length_mm))  # 设置宽度和高度

    # 使用 ImageReader 包装字节流中的条形码图像
    image = ImageReader(barcode_io)

    for i in range(quantity):
        # 每一页只显示一个条形码
        c.setFont("Helvetica", 2)  # 设置字体较小，以适应页面
        # 条形码图片的位置和大小
        c.drawImage(image, 10, length_mm - 25, width=width_mm - 20, height=20)  # 条形码的位置

        # 绘制 SKU 信息
        c.setFont("Helvetica", 6)  # 调整字体大小

        # 添加一页后继续
        if (i + 1) % 1 == 0:
            c.showPage()  # 换页

    # 保存 PDF
    c.save()

    # 确保文件保存成功
    if os.path.exists(pdf_path):
        print(f"文件已成功保存：{pdf_path}")
    else:
        print(f"文件保存失败：{pdf_path}")

# 示例调用
generate_pdf("cs0000000009", 5, 3, 10)  # 宽度5cm，高度3cm，打印10个条形码PDF
