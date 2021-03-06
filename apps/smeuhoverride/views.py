from django.db import connection
from django.shortcuts import render
from tagging.utils import calculate_cloud, LOGARITHMIC


class TagInTheCloud:
    """

    a fake Tag model to feed the cloud
    """
    def __init__(self, name, count, *args):
        self.name = name
        self.count = count


def tag_index(request, template_name="tagging_ext/index.html", *args, **kw):
    query = """
        SELECT tag.name as name, COUNT(tag_item.tag_id) as counter,
               tag_item.tag_id as tag_id
        FROM tagging_taggeditem as tag_item
        INNER JOIN tagging_tag as tag ON (tag.id = tag_item.tag_id)
        GROUP BY tag.name, tag_id
        ORDER BY tag.name
    """
    cursor = connection.cursor()
    cursor.execute(query)

    tags = calculate_cloud(
        [TagInTheCloud(*row) for row in cursor],
        steps=5,
        distribution=LOGARITHMIC
    )

    return render(request, template_name, {'tags': tags})
