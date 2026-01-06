import os
import time
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from action.record import transcribe_audio

bp = Blueprint('transcript', __name__)


@bp.route('/api/transcript', methods=['POST'])
@jwt_required()
def transcript():
    """上传音频文件进行语音识别"""
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "未上传文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "message": "未选择文件"}), 400

    # 保存临时文件
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, f"{datetime.now().timestamp()}_{file.filename}")
    file.save(file_path)

    try:
        # 调用语音识别函数
        text = transcribe_audio(file_path)
        return jsonify({"code": 200, "text": text}), 200
    except ValueError as e:
        return jsonify({"code": 500, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": f"转录失败: {str(e)}"}), 500
    finally:
        # 删除临时文件（添加短暂延迟确保文件完全关闭）
        time.sleep(0.5)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"成功删除临时文件: {file_path}")
        except PermissionError as e:
            print(f"无法删除临时文件 {file_path}: {e}")
        except Exception as e:
            print(f"删除临时文件时出错: {e}")
