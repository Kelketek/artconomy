import { RATINGS } from "@/lib/lib.ts"
import { useViewer } from "./viewer.ts"
import { computed } from "vue"
import type { Asset, FileSpec, RatingsValue } from "@/types/main"
import { AnonUser, User } from "@/store/profiles/types/main"

const getRatingText = (asset: Asset | null) => {
  if (!asset) {
    return ""
  }
  return RATINGS[asset.rating]
}

const getTags = (asset: Asset | null): string[] => {
  return (asset && asset.tags) || []
}

const ICON_EXTENSIONS = [
  "ACC",
  "AE",
  "AI",
  "AN",
  "AVI",
  "BMP",
  "CSV",
  "DAT",
  "DGN",
  "DOC",
  "DOCH",
  "DOCM",
  "DOCX",
  "DOTH",
  "DW",
  "DWFX",
  "DWG",
  "DXF",
  "DXL",
  "EML",
  "EPS",
  "F4A",
  "F4V",
  "FLV",
  "FS",
  "GIF",
  "HTML",
  "IND",
  "JPEG",
  "JPG",
  "JPP",
  "LR",
  "LOG",
  "M4V",
  "MBOX",
  "MDB",
  "MIDI",
  "MKV",
  "MOV",
  "MP3",
  "MP4",
  "MPEG",
  "MPG",
  "MPP",
  "MPT",
  "MPW",
  "MPX",
  "MSG",
  "ODS",
  "OGA",
  "OGG",
  "OGV",
  "ONE",
  "OST",
  "PDF",
  "PHP",
  "PNG",
  "POT",
  "POTH",
  "POTM",
  "POTX",
  "PPS",
  "PPSX",
  "PPT",
  "PPTH",
  "PPTM",
  "PPTX",
  "PREM",
  "PS",
  "PSD",
  "PST",
  "PUB",
  "PUBH",
  "PUBM",
  "PWZ",
  "READ",
  "RP",
  "RTF",
  "SQL",
  "SVG",
  "SWF",
  "TIF",
  "TIFF",
  "TXT",
  "URL",
  "VCF",
  "VDX",
  "VOB",
  "VSD",
  "VSS",
  "VST",
  "VSX",
  "VTX",
  "WAV",
  "WDP",
  "WEBM",
  "WMA",
  "WMV",
  "XD",
  "XLS",
  "XLSM",
  "XLSX",
  "XML",
  "ZIP",
]

export function getExt(filename: string): string {
  filename = filename || ""
  const components = filename.split(".")
  return components[components.length - 1].toUpperCase() as string
}

//
export function isImage(filename: string) {
  return !(
    ["JPG", "BMP", "JPEG", "GIF", "PNG", "SVG"].indexOf(getExt(filename)) === -1
  )
}

//
export function extPreview(filename: string) {
  let ext: string | "UN.KNOWN" = getExt(filename)
  if (ICON_EXTENSIONS.indexOf(ext) === -1) {
    ext = "UN.KNOWN"
  }
  return `/static/icons/${ext}.png`
}

export function thumbFromSpec(thumbName: string, spec: FileSpec) {
  if (!spec) {
    return
  }
  if (
    ["gallery", "full", "preview"].indexOf(thumbName) !== -1 &&
    getExt(spec.full) === "GIF"
  ) {
    return spec.full
  }
  if (spec[thumbName]) {
    return spec[thumbName]
  }
  return spec.full
}

const getDisplayImage = (
  asset: Asset | null,
  thumbName: string,
  isImage: boolean,
  fallbackImage: string,
) => {
  if (!(asset && asset.file)) {
    return fallbackImage
  }
  if (["gallery", "full", "preview"].indexOf(thumbName) === -1) {
    if (asset.preview) {
      return thumbFromSpec("thumbnail", asset.preview)
    }
  }
  if (!isImage) {
    return extPreview(asset.file.full)
  }
  return thumbFromSpec(thumbName, asset.file)
}

const getIsImage = (asset: Asset | null) => {
  if (!(asset && asset.file)) {
    // We'll be returning a default image value.
    return true
  }
  return ["data:image", "svg"].indexOf(asset.file.__type__) !== -1
}

const getBlackListed = (
  asset: Asset | null,
  tags: string[],
  viewer: User | AnonUser,
) => {
  if (!asset) {
    return []
  }
  return tags.filter((n) => viewer.blacklist.includes(n))
}

const getNsfwBlacklisted = (
  asset: Asset | null,
  tags: string[],
  assetRating: RatingsValue,
  viewer: User | AnonUser,
) => {
  if (!asset) {
    return []
  }
  if (!assetRating) {
    return []
  }
  return tags.filter((n) => viewer.nsfw_blacklist.includes(n))
}

const getAssetRating = (asset: Asset | null): RatingsValue => {
  if (!asset) {
    return 0
  }
  return asset.rating
}

const getPermittedRating = (
  asset: Asset | null,
  viewerRating: RatingsValue,
) => {
  if (!asset) {
    return true
  }
  return asset.rating <= viewerRating
}

const getNerfed = (rating: RatingsValue, viewer: User | AnonUser) => {
  return viewer.rating && rating < viewer.rating
}

const getCanDisplay = (
  permittedRating: boolean,
  blacklisted: string[],
  nsfwBlacklisted: string[],
) => {
  if (permittedRating) {
    if (!blacklisted.length && !nsfwBlacklisted.length) {
      return true
    }
  }
  return false
}

declare interface AssetProps {
  asset: Asset | null
  thumbName: string
  fallbackImage: string
}

export const useAssetHelpers = (props: AssetProps) => {
  const { viewer, rating } = useViewer()
  const isImage = computed(() => getIsImage(props.asset))
  const displayImage = computed(() =>
    getDisplayImage(
      props.asset,
      props.thumbName,
      isImage.value,
      props.fallbackImage,
    ),
  )
  const ratingText = computed(() => getRatingText(props.asset))
  const tags = computed(() => getTags(props.asset))
  const assetRating = computed(() => getAssetRating(props.asset))
  const blacklisted = computed(() =>
    getBlackListed(props.asset, tags.value, viewer.value),
  )
  const nsfwBlacklisted = computed(() =>
    getNsfwBlacklisted(
      props.asset,
      tags.value,
      assetRating.value,
      viewer.value,
    ),
  )
  const permittedRating = computed(() =>
    getPermittedRating(props.asset, rating.value),
  )
  const nerfed = computed(() => getNerfed(rating.value, viewer.value))
  const canDisplay = computed(() =>
    getCanDisplay(
      permittedRating.value,
      blacklisted.value,
      nsfwBlacklisted.value,
    ),
  )
  return {
    isImage,
    displayImage,
    ratingText,
    tags,
    assetRating,
    blacklisted,
    nsfwBlacklisted,
    permittedRating,
    nerfed,
    canDisplay,
  }
}

export const defaultFallbackImage = "/static/images/default-avatar.png"

export const assetDefaults = () => ({
  compact: false,
  terse: false,
  popOut: false,
  contain: false,
  fallbackImage: defaultFallbackImage,
})
