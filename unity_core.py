import os
import threading
from UnityPy import AssetsManager
from PIL import Image as PILImage

class UnityBackendCore:
    def __init__(self):
        self.am = None
        self.current_filepath = None
        self.all_textures = {}       # 缓存全部 {name: obj}
        self.filtered_textures = []  # 当前列表展示的贴图名

    def async_load_resource(self, filepath, progress_callback, finish_callback):
        """十一、启用后台线程解析数百MB的大文件，禁止界面卡死"""
        def worker():
            success, msg = self._load_resource_core(filepath, progress_callback)
            finish_callback(success, msg)
        
        threading.Thread(target=worker, daemon=True).start()

    def _load_resource_core(self, filepath, progress_callback):
        """一、四、无视后缀，直接读取内容识别 Unity 资产类型"""
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return False, "文件不存在或为空"
            
        try:
            self.current_filepath = filepath
            progress_callback(0.2, "正在读取底层二进制流...")
            
            # 打开文件句柄
            self.am = AssetsManager(filepath)
            self.all_textures.clear()
            
            # 简单验证是否是有效的 Unity 资产结构
            if not self.am.assets:
                return False, "无法识别为 Unity 资源文件。"
                
            progress_callback(0.6, "正在映射 Texture2D 节点...")
            
            # 遍历资产树
            for asset in self.am.assets:
                for obj in asset.objects.values():
                    if obj.type.name == "Texture2D":
                        try:
                            data = obj.read()
                            name = getattr(data, "m_Name", getattr(data, "name", "Unnamed_Tex"))
                            self.all_textures[name] = obj
                        except Exception:
                            continue # 容错跳过损坏节点
                            
            progress_callback(1.0, "解析完成")
            return True, list(self.all_textures.keys())
            
        except Exception as e:
            return False, f"资源损坏或无法解析: {str(e)}"

    def filter_texture_list(self, only_tex=True, search_query=""):
        """五、筛选与搜索控制（切换时在内存中过滤，不得重新解析文件）"""
        result = []
        query = search_query.lower().strip()
        
        for name in self.all_textures.keys():
            # 仅显示 _tex 过滤
            if only_tex and "_tex" not in name.lower():
                continue
            # 搜索框过滤
            if query and query not in name.lower():
                continue
            result.append(name)
            
        self.filtered_textures = result
        return result

    def get_texture_metadata(self, name):
        """六、七、提取单张贴图明细元数据"""
        obj = self.all_textures.get(name)
        if not obj: return None
        try:
            data = obj.read()
            return {
                "name": name,
                "width": getattr(data, "m_Width", 0),
                "height": getattr(data, "m_Height", 0),
                "format": str(getattr(data, "m_TextureFormat", "Unknown")),
                "mipmap": getattr(data, "m_MipCount", 1) > 1
            }
        except Exception:
            return None

    def get_pil_image(self, name):
        """提取 Pillow 图像对象"""
        obj = self.all_textures.get(name)
        if obj:
            try:
                return obj.read().image
            except Exception:
                return None
        return None

    def async_save_resource(self, out_dir, progress_callback, finish_callback):
        """十、十一、重新注入并打包导出到指定 out 目录，不覆盖原文件"""
        def worker():
            if not self.am or not self.current_filepath:
                finish_callback(False, "没有活跃的修改记录")
                return
                
            try:
                progress_callback(0.3, "正在重新封装 LZ4 压缩块...")
                # 兼容旧版与新版 UnityPy 的封包 API
                packed_data = self.am.file.save() if hasattr(self.am, 'file') and self.am.file else self.am.save()
                
                filename = os.path.basename(self.current_filepath)
                target_path = os.path.join(out_dir, filename)
                
                progress_callback(0.7, "正在写出到输出文件夹...")
                with open(target_path, "wb") as f:
                    f.write(packed_data)
                    
                progress_callback(1.0, "保存成功")
                finish_callback(True, target_path)
            except Exception as e:
                finish_callback(False, f"保存失败: {str(e)}")
                
        threading.Thread(target=worker, daemon=True).start()