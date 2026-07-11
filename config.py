import os
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

class AppConfig:
    def __init__(self):
        # 自动定位手机或电脑的内部私有存储路径
        if platform == 'android':
            from android.storage import app_storage_path
            config_dir = app_storage_path()
        else:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.store = JsonStore(os.path.join(config_dir, 'app_config.json'))

    def is_first_run(self):
        """检查是否是首次启动"""
        return not self.store.exists('paths')

    def get_paths(self):
        """获取输入输出目录"""
        if self.store.exists('paths'):
            data = self.store.get('paths')
            return data.get('in_dir'), data.get('out_dir')
        return None, None

    def save_paths(self, in_dir, out_dir):
        """保存并自动创建目录"""
        try:
            if not os.path.exists(in_dir):
                os.makedirs(in_dir, exist_ok=True)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
                
            self.store.put('paths', in_dir=in_dir, out_dir=out_dir)
            return True, "配置保存成功"
        except Exception as e:
            return False, f"创建目录失败: {str(e)}"