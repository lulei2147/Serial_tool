
class QssTools(object):
    @classmethod
    def set_qss_to_obj(cls, file_path, obj):
        with open(file_path, 'r') as f:
            obj.setStyleSheet(f.read())
