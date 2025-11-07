import os
import base64
import requests
import json
from pathlib import Path
from pdf2image import convert_from_path
from io import BytesIO

# 配置
api = "your vllm devtunnel URL"
port = 8000
input_dir = "input_pdf_folder"
output_dir = "output_folder"

def pdf_to_images(pdf_path):
    """将PDF转换为图片列表"""
    try:
        images = convert_from_path(pdf_path, dpi=200)
        return images
    except Exception as e:
        print(f"PDF转换失败: {e}")
        return []

def encode_image_to_base64(image):
    """将PIL图片编码为base64"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def process_image_with_ocr(image, page_num):
    """处理单个图片页面"""
    # 将图片编码为base64
    image_base64 = encode_image_to_base64(image)
    
    # 构建请求数据
    url = f"{api}/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # 构建消息
    payload = {
        "model": "deepseek-ai/DeepSeek-OCR",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "<image>\n<|grounding|>Convert the document to markdown."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 4096,
        "temperature": 0.1
    }
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取OCR结果
        if "choices" in result and len(result["choices"]) > 0:
            ocr_text = result["choices"][0]["message"]["content"]
            return ocr_text
        else:
            print(f"  ✗ 第{page_num}页响应格式异常")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ 第{page_num}页请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  响应内容: {e.response.text[:200]}")
        return None
    except Exception as e:
        print(f"  ✗ 第{page_num}页处理失败: {e}")
        return None

def process_pdf(pdf_path, output_path):
    """处理单个PDF文件"""
    print(f"正在处理: {pdf_path}")
    
    # 将PDF转换为图片
    print("  转换PDF为图片...")
    images = pdf_to_images(pdf_path)
    
    if not images:
        print("  ✗ PDF转换失败")
        return False
    
    print(f"  共 {len(images)} 页")
    
    # 处理每一页
    all_text = []
    for i, image in enumerate(images, 1):
        print(f"  处理第 {i}/{len(images)} 页...")
        ocr_text = process_image_with_ocr(image, i)
        if ocr_text:
            all_text.append(f"=== 第 {i} 页 ===\n{ocr_text}\n")
        else:
            all_text.append(f"=== 第 {i} 页 ===\n[处理失败]\n")
    
    # 保存结果到output文件夹
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(all_text))
        
        print(f"✓ 成功处理并保存到: {output_path}")
        return True
    except Exception as e:
        print(f"✗ 保存失败: {e}")
        return False

def main():
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有PDF文件
    input_path = Path(input_dir)
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"在 {input_dir} 文件夹中没有找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    print(f"API地址: {api}")
    print("-" * 60)
    
    # 处理每个PDF文件
    success_count = 0
    for pdf_file in pdf_files:
        output_file = Path(output_dir) / f"{pdf_file.stem}.txt"
        if process_pdf(pdf_file, output_file):
            success_count += 1
        print("-" * 60)
    
    print(f"\n处理完成: {success_count}/{len(pdf_files)} 个文件成功")

if __name__ == "__main__":
    main()
