import json

with open("./test.json","r") as f:
    dir = json.load(f)                # .json Ȯ���� ���Ͽ��� ��ųʸ� ���·� ���� ����
    if isinstance(dir,list):          # ���� �޾ƿ��°� ����Ʈ�� ��� ��ųʸ��� �ٲ�
      dir=dict(dir[0])
    print(dir)                        # �� ���� �Ǿ����� Ȯ�ο�




with open("./test1.json","w") as t:   #��ųʸ��� json �������·� ����
    json.dump(dir,t, indent=2)
