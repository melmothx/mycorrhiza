# port of https://metacpan.org/pod/Data::Page
from dataclasses import dataclass
from urllib.parse import urlencode
import unicodedata

@dataclass
class DataPage:
    """Class to manage pages"""
    total_entries: int = 0
    entries_per_page: int = 10
    current_page: int = 1

    def first_page(self):
        return 1

    def last_page(self):
        pages = self.total_entries / self.entries_per_page
        if pages == int(pages):
            last_page = int(pages)
        else:
            last_page = 1 + int(pages)
        if last_page < 1:
            last_page = 1
        return last_page

    def first(self):
        if self.total_entries == 0:
            return 0
        else:
            return int(((self.current_page - 1) * self.entries_per_page) + 1)

    def last(self):
        if self.current_page == self.last_page():
            return int(self.total_entries)
        else:
            return int(self.current_page * self.entries_per_page)

    def previous_page(self):
        if self.current_page > 1:
            return self.current_page - 1
        else:
            return None

    def next_page(self):
        if self.current_page < self.last_page():
            return self.current_page + 1
        else:
            return None

def page_list(pager):
    out = []
    if pager.last_page() == 1:
        return out
    previous_page = pager.previous_page()
    if previous_page:
        out.append({
            "label": "Previous",
            "current": False,
            "page_id": previous_page,
            "class": "page-link page-link-previous",
            "key": "p-previous-" + str(previous_page),
        })

    last_page = pager.last_page()
    for num in range(pager.first_page(), pager.last_page() + 1):
        is_current = pager.current_page == num
        item_class = "page-link page-link-" + str(num)
        if (pager.current_page - num ) > -3 and (pager.current_page - num ) < 3:
            if is_current:
                item_class += ' active'
            struct = {
                "label": num,
                "current": is_current,
                "page_id": num,
                "class": item_class,
                "key": "p-link-" + str(num),
            }
            out.append(struct)

    if not any(el['page_id'] == 1 for el in out):
        out.insert(0, {
            "label": "First",
            "current": False,
            "page_id": 1,
            "class": "page-link page-link-1",
            "key": "p-first-1",
        })

    next_page = pager.next_page()
    if next_page:
        out.append({
            "label": "Next",
            "current": False,
            "page_id": next_page,
            "class": "page-link page-link-next",
            "key": "p-next-" + str(next_page),
        })

    if not any(el['page_id'] == last_page for el in out):
        out.append({
            "label": "Last",
            "current": False,
            "page_id": last_page,
            "class": "page-link page-link-" + str(last_page),
            "key": "p-last-" + str(last_page),
        })

    return out

def paginator(pager, base_url, params):
    out = []
    common = []
    for param in params:
        if param != "page_number":
            for value in params.getlist(param):
                common.append((param, value))

    # nothing to show
    if pager.last_page() == 1:
        return None

    if pager.previous_page():
        out.append({
            "label": "Previous",
            "current": False,
            "url": get_paged_url(base_url, common, pager.previous_page()),
            "class": "page-link page-link-previous"
        })

    for num in range(pager.first_page(), pager.last_page() + 1):
        struct = {
            "label": num,
            "current": pager.current_page == num,
            "url": get_paged_url(base_url, common, num),
            "class": "page-link page-link-" + str(num)
        }
        out.append(struct)

    if pager.next_page():
        out.append({
            "label": "Next",
            "current": False,
            "url": get_paged_url(base_url, common, pager.next_page()),
            "class": "page-link page-link-next"
        })

    return out

def get_paged_url(base_url, common, num):
    query = common.copy()
    query.append(("page_number", num))
    return base_url + '?' + urlencode(query)

def log_user_operation(user, op, canonical, alias):
    if user and op and canonical:
        canonical_title = "canonical"
        alias_title = "alias"
        canonical_data = None
        if "translation" in op:
            canonical_title = "original"
            alias_title = "translation"
        elif "aggregation" in op:
            canonical_title = "aggregation"
            alias_title = "aggregated"
        elif "exclusion" in op:
            canonical_title = "excluded"
            alias_title = "excluded"
        elif op.startswith("before-update-") or op.startswith("after-update-"):
            canonical_title = op
            canonical_data = canonical.as_api_dict()
            if alias:
                raise Exception("Alias argument should be None for {}".format(op))

        if alias:
            comment = "{}: {} ({})\n{}: {} ({})".format(canonical_title, canonical.display_name(), canonical.id,
                                                        alias_title, alias.display_name(), alias.id)
            alias.changelogs.create(
                user=user,
                username=user.username,
                operation=op,
                comment=comment,
            )
        else:
            comment = "{}: {} ({})".format(canonical_title, canonical.display_name(), canonical.id)

        canonical.changelogs.create(
            user=user,
            username=user.username,
            operation=op,
            comment=comment,
            object_data=canonical_data,
        )

def strip_diacritics(s):
    if isinstance(s, str):
        return ''.join(c for c in unicodedata.normalize('NFKD', s) if unicodedata.category(c) != 'Mn')
    elif s:
        return str(s)
    else:
        return ''
