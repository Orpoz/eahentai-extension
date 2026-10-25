package eu.kanade.tachiyomi.extension.en.eahentai

import eu.kanade.tachiyomi.source.model.Filter
import eu.kanade.tachiyomi.source.model.FilterList
import eu.kanade.tachiyomi.source.model.MangasPage
import eu.kanade.tachiyomi.source.model.Page
import eu.kanade.tachiyomi.source.model.SChapter
import eu.kanade.tachiyomi.source.model.SManga
import eu.kanade.tachiyomi.source.model.SMangaUpdate
import keiyoushi.annotation.Source
import keiyoushi.network.get
import keiyoushi.network.rateLimit
import keiyoushi.source.KeiSource
import keiyoushi.utils.firstInstanceOrNull
import keiyoushi.utils.parseAs
import kotlinx.serialization.json.JsonElement
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient

@Source
abstract class Eahentai : KeiSource() {

    private val apiUrl by lazy { "$baseUrl/api/image".toHttpUrl() }

    override fun OkHttpClient.Builder.configureClient(): OkHttpClient.Builder = rateLimit(permits = 4)

    override suspend fun getPopularManga(page: Int): MangasPage = popular(page, "views_daily")

    // The popular endpoint returns a bare array with no page count.
    private suspend fun popular(page: Int, orderBy: String): MangasPage {
        val url = apiUrl.newBuilder()
            .addPathSegments("popular/")
            .addQueryParameter("page", (page - 1).toString())
            .addQueryParameter("take", PAGE_SIZE.toString())
            .addQueryParameter("orderby", orderBy)
            .build()
        val albums = client.get(url).parseAs<List<AlbumDto>>()
        return MangasPage(albums.toSMangas(), albums.size >= PAGE_SIZE)
    }

    override suspend fun getLatestUpdates(page: Int): MangasPage {
        val url = apiUrl.newBuilder()
            .addPathSegments("latest/")
            .addQueryParameter("page", (page - 1).toString())
            .addQueryParameter("take", PAGE_SIZE.toString())
            .build()
        return client.get(url).parseAs<PagedAlbumsDto>().toMangasPage(page)
    }

    override suspend fun getSearchMangaList(page: Int, query: String, filters: FilterList): MangasPage {
        val sort = filters.firstInstanceOrNull<SortFilter>()?.toUriPart() ?: "date_desc"
        val type = filters.firstInstanceOrNull<SearchTypeFilter>()?.toUriPart() ?: "gallery"
        val q = query.trim()

        // The search endpoints return nothing for an empty query, so fall back to the plain listings.
        if (q.isEmpty()) {
            return if (sort == "date_desc") getLatestUpdates(page) else popular(page, sort)
        }

        val url = apiUrl.newBuilder().apply {
            if (type == "gallery") {
                addPathSegments("search/v2/")
            } else {
                addPathSegments("entities/albums")
            }
            addQueryParameter("type", type)
            addQueryParameter("q", q)
            addQueryParameter("page", (page - 1).toString())
            addQueryParameter("take", PAGE_SIZE.toString())
            addQueryParameter("orderby", sort)
        }.build()
        return client.get(url).parseAs<PagedAlbumsDto>().toMangasPage(page)
    }

    override suspend fun getMangaByUrl(url: HttpUrl): SManga? {
        if (url.host != baseUrl.toHttpUrl().host || url.pathSegments.firstOrNull() != "a") return null
        val id = url.pathSegments.getOrNull(1)?.toIntOrNull() ?: return null
        return fetchAlbum(id.toString())?.toDetailedSManga()
    }

    override fun getMangaUrl(manga: SManga): String = "$baseUrl/a/${manga.url}"

    override fun getChapterUrl(chapter: SChapter): String = "$baseUrl/a/${chapter.url}/0"

    override suspend fun fetchMangaUpdate(
        manga: SManga,
        chapters: List<SChapter>,
        fetchDetails: Boolean,
        fetchChapters: Boolean,
    ): SMangaUpdate {
        val album = fetchAlbum(manga.url) ?: throw Exception("Gallery not found or removed")
        return SMangaUpdate(album.toDetailedSManga(), listOf(album.toSChapter()))
    }

    override suspend fun getPageList(chapter: SChapter): List<Page> {
        val album = fetchAlbum(chapter.url) ?: return emptyList()
        return album.pageUrls().mapIndexed { index, url -> Page(index, imageUrl = url) }
    }

    override fun getFilterList(data: JsonElement?): FilterList = FilterList(
        Filter.Header("With an empty query, sort picks the listing"),
        SortFilter(),
        SearchTypeFilter(),
    )

    private suspend fun fetchAlbum(id: String): AlbumDto? {
        val url = apiUrl.newBuilder().addPathSegment("album").addPathSegment(id).build()
        return client.get(url).parseAs<List<AlbumDto>>().firstOrNull()?.takeUnless { it.isSoftDeleted }
    }

    private fun List<AlbumDto>.toSMangas() = filterNot { it.isSoftDeleted }.map { it.toSManga() }

    private fun PagedAlbumsDto.toMangasPage(page: Int) = MangasPage(items.toSMangas(), page < totalPages)

    companion object {
        private const val PAGE_SIZE = 42
    }
}
