from tortoise import Model, fields


class Users(Model):
    id = fields.IntField(pk=True)
    password = fields.TextField()
    username = fields.CharField(max_length=150)
    is_superuser = fields.BooleanField(default=0)
    is_active = fields.BooleanField(default=0)

    def __str__(self):
        return self.username


class Products(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    description = fields.TextField()
    price = fields.BigIntField()


class BankAccounts(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='account', on_delete=fields.CASCADE)
    bill_id = fields.UUIDField(unique=True)
    balance = fields.BigIntField()


class Transactions(Model):
    id = fields.BigIntField(pk=True)
    bill_id = fields.ForeignKeyField('models.BankAccounts', related_name='transaction', on_delete=fields.CASCADE)
    amount = fields.BigIntField()
    date = fields.DatetimeField(auto_now_add=True)