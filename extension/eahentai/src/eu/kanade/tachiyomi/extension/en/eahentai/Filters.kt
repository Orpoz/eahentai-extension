package eu.kanade.tachiyomi.extension.en.eahentai

import eu.kanade.tachiyomi.source.model.Filter

open class UriPartFilter(displayName: String, private val vals: Array<Pair<String, String>>) :
    Filter.Select<String>(displayName, vals.map { it.first }.toTypedArray()) {
    fun toUriPart() = vals[state].second
}

class SortFilter :
    UriPartFilter(
        "Sort by",
        arrayOf(
            "Newest" to "date_desc",
            "Popular today" to "views_daily",
            "Popular this week" to "views_weekly",
            "Popular this month" to "views_monthly",
            "Popular all time" to "views_alltime",
        ),
    )

class SearchTypeFilter :
    UriPartFilter(
        "Search in",
        arrayOf(
            "Title / tags" to "gallery",
            "Artist (exact name)" to "artist",
            "Parody (exact name)" to "parody",
            "Character (exact name)" to "character",
        ),
    )
