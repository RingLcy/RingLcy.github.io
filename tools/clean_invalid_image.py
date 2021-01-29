import os

post_dir = "../_posts"
img_dir = "../assets/img"

img_list = []
for each_file in os.listdir(img_dir):
    if (os.path.isdir(os.path.join(img_dir, each_file))):
        continue
    img_list.append(each_file)

valid_img_list = []
for each_file in os.listdir(post_dir):
    with open(os.path.join(post_dir, each_file), encoding="utf-8") as fh:
        data = fh.read()
        for img in img_list:
            if img not in valid_img_list and img in data:
                valid_img_list.append(img)

for img in img_list:
    if img not in valid_img_list:
        os.remove(os.path.join(img_dir, img))
        # print(img)

