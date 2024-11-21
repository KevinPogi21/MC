"""Cascade

Revision ID: f25ef2541c9f
Revises: 88d330676c4f
Create Date: 2024-11-20 19:48:31.953878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f25ef2541c9f'
down_revision = '88d330676c4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Notification', schema=None) as batch_op:
        batch_op.drop_constraint('Notification_booking_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Booking', ['booking_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('Review_Images', schema=None) as batch_op:
        batch_op.drop_constraint('Review_Images_rr_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Reviews_Rating', ['rr_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('Reviews_Rating', schema=None) as batch_op:
        batch_op.drop_constraint('Reviews_Rating_tour_guide_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Tour_Guide', ['tour_guide_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('Tour_Guide', schema=None) as batch_op:
        batch_op.drop_constraint('Tour_Guide_user_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('Tour_Guide_toperator_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Tour_Operator', ['toperator_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'Users', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('Tour_Operator', schema=None) as batch_op:
        batch_op.drop_constraint('Tour_Operator_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Users', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tour_count', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.drop_column('tour_count')

    with op.batch_alter_table('Tour_Operator', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Tour_Operator_user_id_fkey', 'Users', ['user_id'], ['id'])

    with op.batch_alter_table('Tour_Guide', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Tour_Guide_toperator_id_fkey', 'Tour_Operator', ['toperator_id'], ['id'])
        batch_op.create_foreign_key('Tour_Guide_user_id_fkey', 'Users', ['user_id'], ['id'])

    with op.batch_alter_table('Reviews_Rating', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Reviews_Rating_tour_guide_id_fkey', 'Tour_Guide', ['tour_guide_id'], ['id'])

    with op.batch_alter_table('Review_Images', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Review_Images_rr_id_fkey', 'Reviews_Rating', ['rr_id'], ['id'])

    with op.batch_alter_table('Notification', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Notification_booking_id_fkey', 'Booking', ['booking_id'], ['id'])

    # ### end Alembic commands ###
