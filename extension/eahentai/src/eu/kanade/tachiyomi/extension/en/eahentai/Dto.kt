package eu.kanade.tachiyomi.extension.en.eahentai

import eu.kanade.tachiyomi.source.model.SChapter
import eu.kanade.tachiyomi.source.model.SManga
import eu.kanade.tachiyomi.source.model.UpdateStrategy
import keiyoushi.utils.tryParseDateTime
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import okhttp3.HttpUrl.Companion.toHttpUrl
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

@Serializable
class PagedAlbumsDto(
    val items: List<AlbumDto>,
    val totalPages: Int,
)

@Serializable
class AlbumDto(
    @SerialName("albumID") private val albumId: Int,
    private val title: String,
    private val thumbnailUri: String? = null,
    private val addDt: String? = null,
    private val tags: String? = null,
    private val characters: String? = null,
    private val from: String? = null,
    private val author: String? = null,
    private val albumType: String? = null,
    val isSoftDeleted: Boolean = false,
    private val images: List<ImageDto> = emptyList(),
) {
    fun toSManga() = SManga.create().apply {
        url = albumId.toString()
        title = this@AlbumDto.title
        thumbnail_url = thumbnailUri?.let(::cdnUrl)
    }

    fun toDetailedSManga() = toSManga().apply {
        val authors = this@AlbumDto.author.splitPipe().filterNot { it == "unknown artist" }
        artist = authors.joinToString().ifEmpty { null }
        author = artist
        genre = (albumType.splitPipe() + tags.splitPipe()).joinToString()
        description = buildString {
            from.splitPipe().filterNot { it == "original" }.takeIf { it.isNotEmpty() }
                ?.let { append("Parody: ", it.joinToString(), "\n") }
            characters.splitPipe().takeIf { it.isNotEmpty() }
                ?.let { append("Characters: ", it.joinToString(), "\n") }
            if (images.isNotEmpty()) append("Pages: ", images.size)
        }.trim().ifEmpty { null }
        status = SManga.COMPLETED
        update_strategy = UpdateStrategy.ONLY_FETCH_ONCE
    }

    fun toSChapter() = SChapter.create().apply {
        url = albumId.toString()
        name = "Gallery"
        chapter_number = 1f
        date_upload = DATE_FORMAT.tryParseDateTime(addDt, ZoneOffset.UTC)
    }

    fun pageUrls(): List<String> = images.sortedBy { it.sort }.map { cdnUrl(it.imageUri) }
}

@Serializable
class ImageDto(
    val imageUri: String,
    val sort: Int,
)

private fun String?.splitPipe(): List<String> = this?.split('|')?.map(String::trim)?.filter(String::isNotEmpty).orEmpty()

private fun cdnUrl(uri: String): String = CDN_URL.newBuilder().addPathSegments(uri).build().toString()

private val CDN_URL = "https://i.eahentai.com/file/ea-gallery".toHttpUrl()

private val DATE_FORMAT = DateTimeFormatter.ISO_LOCAL_DATE_TIME
