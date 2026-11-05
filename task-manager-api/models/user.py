from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from utils.constants import Role
from utils.helpers import utcnow


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=Role.USER)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    # Excluir o usuário remove suas tasks na mesma transação.
    tasks = db.relationship('Task', back_populates='user', cascade='save-update, merge, delete')

    # ---- domínio -------------------------------------------------------

    def to_dict(self):
        """Serialização pública: nunca inclui o hash da senha."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        try:
            return check_password_hash(self.password, raw_password)
        except ValueError:  # hash em formato legado/desconhecido
            return False

    def is_admin(self):
        return self.role == Role.ADMIN

    # ---- acesso a dados ------------------------------------------------

    @classmethod
    def get_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def get_by_email(cls, email):
        return db.session.execute(db.select(cls).filter_by(email=email)).scalar_one_or_none()

    @classmethod
    def list_all(cls):
        return db.session.execute(db.select(cls).order_by(cls.id)).scalars().all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(db.select(func.count(cls.id)))
