import json
import pytchat


class CommentHandler:
    def __init__(self, video_id):
        self.chat = pytchat.create(
            video_id=video_id,
            interruptable=False,
        )
    
    def get_comment(self):
        comments = self.__get_comments()
        if comments is None:
            return None
        
        comment = comments[-1]  # Latest comment
        message = comment.get("message")

        return message
    
    def __get_comments(self):
        if not self.chat.is_alive():
            print("Comment handler is not started.")
            return None
        
        comments = json.loads(self.chat.get().json())
        if not comments:
            print("Could not capture any comments.")
            return None
        
        return comments
