from dataclasses import dataclass

from slugify import slugify

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe import TagOut
from mealie.schema.recipe.recipe_category import CategorySave, TagSave


class NoContextException(Exception):
    pass


@dataclass(slots=True)
class ScraperContext:
    repos: AllRepositories


class ScrapedExtras:
    def __init__(self) -> None:
        self._tags: list[str] = []
        self._category: str = ""

    def set_tags(self, tags: list[str]) -> None:
        self._tags = tags

    def set_category(self, category: str) -> None:
        self._category = category

    def use_tags(self, ctx: ScraperContext) -> list[TagOut]:
        if not self._tags:
            return []

        repo = ctx.repos.tags

        tags = []
        seen_tag_slugs: set[str] = set()
        for tag in self._tags:
            slugify_tag = slugify(tag)
            if slugify_tag in seen_tag_slugs:
                continue

            seen_tag_slugs.add(slugify_tag)

            # Check if tag exists
            if db_tag := repo.get_one(slugify_tag, "slug"):
                tags.append(db_tag)
                continue

            save_data = TagSave(name=tag, group_id=ctx.repos.group_id)
            db_tag = repo.create(save_data)

            tags.append(db_tag)

        return tags

    def use_category(self, ctx: ScraperContext) -> list[TagOut]:
        if not self._category:
            return []

        repo = ctx.repos.categories

        # Split comma-separated categories if category is improperly used
        category_list = [cat.strip() for cat in self._category.split(",")] if isinstance(self._category, str) else [self._category]

        categories = []
        seen_category_slugs: set[str] = set()
        for category in category_list:
            if not category:
                continue
                
            slugify_category = slugify(category)
            if slugify_category in seen_category_slugs:
                continue

            seen_category_slugs.add(slugify_category)

            # Check if category exists
            if db_category := repo.get_one(slugify_category, "slug"):
                categories.append(db_category)
                continue

            save_data = CategorySave(name=category, group_id=ctx.repos.group_id)
            db_category = repo.create(save_data)

            categories.append(db_category)

        return categories
