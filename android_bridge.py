import os
from kivy.utils import platform

class AndroidBridge:
    @staticmethod
    def save_to_gallery(pil_image, filename_prefix):
        """八、使用 Android MediaStore API 安全保存到系统相册，防止分区存储报错"""
        if platform != 'android':
            # 电脑测试环境下的兜底机制
            desktop_path = os.path.expanduser("~/Pictures")
            os.makedirs(desktop_path, exist_ok=True)
            out_path = os.path.join(desktop_path, f"{filename_prefix}.png")
            pil_image.save(out_path, "PNG")
            return True, f"已保存到电脑图片目录:\n{out_path}"

        try:
            # 动态绑定安卓原生 Java 类
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = PythonActivity.mActivity

            ContentValues = autoclass('android.content.ContentValues')
            MediaStore = autoclass('android.provider.MediaStore')
            BitmapFactory = autoclass('android.graphics.BitmapFactory')
            CompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
            
            # 1. 先把 Pillow Image 转为字节并存为临时文件以加载为 Java Bitmap
            temp_path = os.path.join(current_activity.getCacheDir().getAbsolutePath(), "temp_export.png")
            pil_image.save(temp_path, "PNG")
            java_bitmap = BitmapFactory.decodeFile(temp_path)
            
            # 2. 构造 MediaStore 元数据
            values = ContentValues()
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, f"{filename_prefix}_{os.urandom(2).hex()}")
            values.put(MediaStore.MediaColumns.MIME_TYPE, "image/png")
            values.put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/UnityTextureTool")
            
            # 3. 插入相册流
            resolver = current_activity.getContentResolver()
            image_uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            
            if image_uri is None:
                return False, "创建相册媒体节点失败"
                
            out_stream = resolver.openOutputStream(image_uri)
            java_bitmap.compress(CompressFormat.PNG, 100, out_stream)
            out_stream.flush()
            out_stream.close()
            
            # 删除缓存
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return True, "✨ 贴图成功保存至系统图库！"
        except Exception as e:
            return False, f"相册写入失败: {str(e)}"