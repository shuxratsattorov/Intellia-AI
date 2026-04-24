class RedisKeys:
 
    # --- OTP ----------------------------------------------------------------
 
    @staticmethod
    def otp(flow: str, user_id: int | str) -> str:
        return f"auth:otp:{flow}:{user_id}"
 
    # --- Attempts -----------------------------------------------------------
 
    @staticmethod
    def attempts_otp(flow: str, user_id: int | str) -> str:
        return f"auth:attempts_otp:{flow}:{user_id}"
 
    @staticmethod
    def attempts_login(user_id: int | str) -> str:
        return f"auth:attempts:login:{user_id}"
 
    # --- Resend -------------------------------------------------------------
 
    @staticmethod
    def resend_otp(flow: str, user_id: int | str) -> str:
        return f"auth:resend_otp:{flow}:{user_id}"
 
    # --- Cooldown -----------------------------------------------------------
 
    @staticmethod
    def cooldown_otp(flow: str, user_id: int | str) -> str:
        return f"auth:cooldown_otp:{flow}:{user_id}"
 
    # --- Block --------------------------------------------------------------
 
    @staticmethod
    def block_otp(flow: str, user_id: int | str) -> str:
        return f"auth:block_otp:{flow}:{user_id}"
 
    @staticmethod
    def block_login(user_id: int | str) -> str:
        return f"auth:block:login:{user_id}"
