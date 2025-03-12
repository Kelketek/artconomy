<template>
  <v-container fluid class="pa-0">
    <div v-if="isRegistered" class="px-3">
      <v-img
        :src="randomBanner.src.href"
        aspect-ratio="7.2"
        alt="Welcome back to Artconomy!"
        :eager="prerendering"
      />
      <div class="text-right pr-2 elevation-2 credit-overlay">
        <small>
          <ac-link
            :to="{
              name: 'AboutUser',
              params: { username: randomBanner.artist },
            }"
            >Art by {{ randomBanner.artist }}
          </ac-link>
        </small>
      </div>
    </div>
    <v-container v-if="!isRegistered">
      <v-row no-gutters>
        <v-col class="text-center px-2" cols="12">
          <h1>
            Your ideas. <br class="hidden-sm-and-up" />
            Your characters. Realized.
          </h1>
        </v-col>
        <v-col cols="8" offset="2" lg="4" offset-lg="4">
          <ac-bound-field
            :field="searchForm.fields.q"
            label="I'm looking for..."
            class="home-search-field"
            :prepend-icon="mdiMagnify"
            @keyup="searchFromField"
          />
        </v-col>
        <v-col class="text-center" cols="12" lg="6" offset-lg="3">
          Try terms like:
          <v-chip
            v-for="term in searchTerms"
            :key="term"
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search({ q: term })"
          >
            {{ term }}
          </v-chip>
        </v-col>
        <v-col class="text-center text-lg-right pt-3 px-lg-2" cols="12" lg="6">
          <v-btn color="primary" variant="flat" @click="search({})">
            <v-icon left :icon="mdiMagnify" />
            Browse Everyone Open
          </v-btn>
        </v-col>
        <v-col class="text-center text-lg-left pt-3 px-lg-2" cols="12" lg="6">
          <v-btn
            color="secondary"
            :to="{ name: 'LandingArtistTools' }"
            variant="flat"
          >
            <v-icon left :icon="mdiPalette" />
            Are you an artist?
          </v-btn>
        </v-col>
      </v-row>
      <v-row no-gutters class="pt-2">
        <v-col class="text-center d-flex" cols="12" md="4">
          <v-row no-gutters>
            <v-col class="grow pa-1">
              <v-row no-gutters>
                <v-col cols="6" md="12" order="2" order-md="1">
                  <v-img
                    :src="laptop"
                    max-height="20vh"
                    aspect-ratio="1"
                    contain
                    alt="Vulpy the Artfox typing away on a Laptop"
                    :eager="true"
                    :transition="false"
                  />
                </v-col>
                <v-col cols="6" md="12" order="1" order-md="2">
                  <v-row
                    no-gutters
                    class="justify-content fill-height"
                    align="center"
                  >
                    <v-col class="pa-1">
                      Find an artist you want to commission, and place an order
                      describing what you want.
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
        <v-col class="text-center d-flex" cols="12" md="4">
          <v-row no-gutters>
            <v-col class="grow pa-1">
              <v-row no-gutters>
                <v-col cols="6" md="12">
                  <v-img
                    :src="fingerPainting"
                    max-height="20vh"
                    aspect-ratio="1"
                    contain
                    alt="Vulpy the Artfox painting a piece of art."
                    :eager="true"
                    :transition="false"
                  />
                </v-col>
                <v-col class="pa-1" cols="6" md="12">
                  <v-row
                    no-gutters
                    class="justify-content fill-height"
                    align="center"
                  >
                    <v-col>
                      <p>
                        We hold onto your payment until the work is done. In the
                        event the artist fails to complete the assignment,
                        you'll get your money back!*
                      </p>
                      <p>
                        <small
                          >* Protection available only on
                          <router-link
                            :to="{
                              name: 'BuyAndSell',
                              params: { question: 'shield' },
                            }"
                            >Artconomy Shield
                          </router-link>
                          <v-icon
                            color="green"
                            class="px-1"
                            :icon="mdiShieldHalfFull"
                          />
                          enabled products.</small
                        >
                      </p>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
        <v-col class="text-center d-flex" cols="12" md="4">
          <v-row no-gutters>
            <v-col class="grow pa-1">
              <v-row dense>
                <v-col cols="6" md="12" order="2" order-md="1">
                  <v-img
                    :src="fridge"
                    max-height="20vh"
                    aspect-ratio="1"
                    contain
                    alt="Vulpy the Artfox hanging his work on the fridge for all to enjoy!"
                    :eager="true"
                    :transition="false"
                  />
                </v-col>
                <v-col cols="6" md="12" order="1" order-md="2">
                  <v-row class="justify-content fill-height" align="center">
                    <v-col>
                      <p>
                        Once completed, you can catalog and show off your
                        completed piece to the world! If you have a character,
                        you can add it to your character's gallery, too!
                      </p>
                      <p>
                        <small
                          >Vulpy images by
                          <a
                            target="_blank"
                            href="https://artconomy.com/profile/Halcyon/products/"
                            >Halcyon</a
                          ></small
                        >
                      </p>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
    <v-container fluid :class="{ 'pt-0': isRegistered }">
      <v-row no-gutters>
        <v-col cols="12" :order="featuredOrder" class="pt-1">
          <v-card>
            <ac-tabs
              v-model="mainSection"
              :items="mainSectionItems"
              label="Categories"
            />
          </v-card>
          <v-window v-model="mainSection">
            <v-window-item :value="0">
              <div>
                <v-row v-if="featured.x">
                  <v-col
                    class="text-left align-content-center align-left justify-start d-flex pt-5 pl-5"
                  >
                    <ac-avatar
                      :user="featured.x"
                      :inline="true"
                      :show-name="false"
                      class="d-inline-block"
                    />
                    <div class="text-h4 d-inline-block pl-3">
                      {{ featured.x.username }}
                    </div>
                  </v-col>
                </v-row>
                <v-card-text v-else>
                  Artists featured for quality and performance!
                </v-card-text>
              </div>
              <v-row>
                <v-col
                  v-if="
                    featured.x &&
                    display.mdAndUp.value &&
                    featured.x.submissions[0]
                  "
                  cols="12"
                  md="3"
                >
                  <ac-gallery-preview
                    :submission="featured.x.submissions[0]"
                    :show-footer="false"
                  />
                </v-col>
                <v-col cols="12" md="9">
                  <v-row v-if="featured.x" justify="center">
                    <v-spacer />
                    <template v-if="featured.x.products.length">
                      <v-col
                        v-for="product in featured.x.products"
                        :key="product.id"
                        cols="6"
                        md="3"
                      >
                        <ac-product-preview :product="product" />
                      </v-col>
                    </template>
                    <template v-else-if="slicedFeaturedSubmissions">
                      <v-col
                        v-for="submission in slicedFeaturedSubmissions"
                        :key="submission.id"
                        cols="6"
                        md="3"
                      >
                        <ac-gallery-preview
                          :submission="submission"
                          :show-footer="false"
                        />
                      </v-col>
                    </template>
                    <v-spacer />
                    <v-col cols="12">
                      <v-row>
                        <v-col cols="6">
                          <v-btn
                            block
                            color="secondary"
                            variant="flat"
                            @click="search({ featured: true })"
                          >
                            See All Featured
                          </v-btn>
                        </v-col>
                        <v-col cols="6">
                          <v-btn
                            block
                            color="primary"
                            :to="profileLink(featured.x) as RouteLocationRaw"
                          >
                            Full Profile
                          </v-btn>
                        </v-col>
                      </v-row>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-window-item>
            <v-window-item :value="1">
              <v-card-text
                >Products by artists given high ratings by previous
                commissioners</v-card-text
              >
              <ac-product-slider :list="rated" />
              <v-btn
                block
                color="primary"
                variant="flat"
                @click="search({ rating: true })"
              >
                See More
              </v-btn>
            </v-window-item>
            <v-window-item :value="2">
              <v-card-text>
                Looking for something lower-budget? Check out these offerings
                from our artists, $30 or less!
              </v-card-text>
              <ac-product-slider :list="lowPriced" />
              <v-btn
                block
                color="primary"
                class="low-price-more"
                variant="flat"
                @click="search({ max_price: '30.00' })"
              >
                See More
              </v-btn>
            </v-window-item>
            <v-window-item :value="3">
              <v-card-text
                >Feeling lucky? Here are some offers from our artists at
                random!</v-card-text
              >
              <ac-product-slider :list="randomProducts" />
              <v-btn color="primary" block variant="flat" @click="search({})">
                Browse Everyone Open
              </v-btn>
            </v-window-item>
          </v-window>
        </v-col>
        <v-col
          cols="12"
          md="12"
          :lg="isRegistered ? 12 : 6"
          :class="{ 'py-2': !isRegistered }"
          :order="isRegistered ? 1 : 5"
          :order-lg="isRegistered ? 1 : 2"
        >
          <v-card :color="theme.current.value.colors['well-darken-4']">
            <v-toolbar dense color="secondary">
              <v-toolbar-title>Recent Commissions</v-toolbar-title>
              <v-spacer />
              <v-toolbar-items>
                <v-btn
                  color="primary"
                  class="search-commissions"
                  variant="flat"
                  @click="searchSubmissions({ commissions: true })"
                >
                  See More
                </v-btn>
              </v-toolbar-items>
            </v-toolbar>
            <v-card-text
              >Commissions recently completed by our artists</v-card-text
            >
            <ac-load-section :controller="commissions">
              <template #default>
                <v-row dense>
                  <v-col
                    v-for="submission in commissionsList"
                    :key="submission.x!.id"
                    cols="6"
                    sm="4"
                    md="3"
                    :lg="isRegistered ? 2 : 4"
                  >
                    <ac-gallery-preview
                      :submission="submission.x"
                      :show-footer="false"
                    />
                  </v-col>
                </v-row>
              </template>
              <template #loading-spinner>
                <v-row dense>
                  <v-col
                    v-for="i in Array(listSizer(true)).keys()"
                    :key="i"
                    cols="6"
                    sm="4"
                    md="3"
                    :lg="isRegistered ? 2 : 4"
                  >
                    <v-responsive
                      aspect-ratio="1"
                      max-height="100%"
                      max-width="100%"
                    >
                      <v-skeleton-loader max-height="100%" type="image" />
                    </v-responsive>
                  </v-col>
                </v-row>
              </template>
            </ac-load-section>
          </v-card>
        </v-col>
        <v-col
          cols="12"
          md="12"
          :lg="6"
          class="px-1 py-2 fill-height"
          order="2"
          order-lg="3"
        >
          <v-card :color="theme.current.value.colors['well-darken-4']">
            <v-toolbar dense color="secondary">
              <v-toolbar-title>Community Resources</v-toolbar-title>
            </v-toolbar>
            <v-row no-gutters>
              <v-col
                cols="6"
                md="3"
                lg="6"
                class="text-center"
                align-self="center"
              >
                <v-img
                  :src="discord"
                  :aspect-ratio="3 / 2"
                  contain
                  alt="Discord"
                  :eager="prerendering"
                />
              </v-col>
              <v-col
                cols="6"
                md="3"
                lg="6"
                class="text-center"
                align-self="center"
              >
                <v-responsive :aspect-ratio="3 / 2" class="pa-1">
                  <v-row no-gutters justify="center" class="fill-height">
                    <v-col align-self="center">
                      <p>
                        <strong
                          >Want your voice to be heard, to network with artists,
                          and meet new friends?</strong
                        >
                      </p>
                      <p>Check out our Discord!</p>
                      <v-btn
                        href="https://discord.gg/4nWK9mf"
                        target="_blank"
                        rel="nofollow,noopener"
                        color="primary"
                        variant="flat"
                      >
                        Join now!
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-responsive>
              </v-col>
              <v-col cols="6" md="3" lg="6" align-self="center">
                <v-col class="text-center">
                  <a
                    :href="articles[0].link"
                    target="_blank"
                    :aria-label="articles[0].title"
                  >
                    <v-img
                      :src="articles[0].image"
                      alt=""
                      :aspect-ratio="3 / 2"
                      contain
                      :eager="prerendering"
                    />
                  </a>
                </v-col>
                <v-col class="text-center">
                  <strong>
                    <a
                      id="article-0-link"
                      :href="articles[0].link"
                      target="_blank"
                      >{{ articles[0].title }}</a
                    >
                  </strong>
                </v-col>
              </v-col>
              <v-col cols="6" md="3" lg="6" align-self="center">
                <v-col class="text-center">
                  <a
                    :href="articles[1].link"
                    target="_blank"
                    :aria-label="articles[0].title"
                  >
                    <v-img
                      :src="articles[1].image"
                      alt=""
                      :aspect-ratio="3 / 2"
                      contain
                      :eager="prerendering"
                    />
                  </a>
                </v-col>
                <v-col class="text-center">
                  <strong>
                    <a
                      id="article-1-link"
                      :href="articles[1].link"
                      target="_blank"
                      >{{ articles[1].title }}</a
                    >
                  </strong>
                </v-col>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
        <v-col
          cols="12"
          class="text-center"
          order="3"
          :order-lg="isRegistered ? 5 : 4"
        >
          <v-card color="secondary">
            <v-card-text class="text-center">
              <h2>Find Your Community</h2>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" order="4" order-lg="5">
          <v-card>
            <ac-tabs
              v-model="communitySection"
              :items="communityItems"
              label="Communities"
            />
          </v-card>
          <v-window v-model="communitySection">
            <v-window-item :value="0">
              <ac-product-slider :list="artistsOfColor" />
              <v-btn
                block
                color="primary"
                variant="flat"
                @click="search({ artists_of_color: true })"
              >
                See More
              </v-btn>
            </v-window-item>
            <v-window-item :value="1">
              <ac-product-slider :list="lgbt" />
              <v-btn
                block
                color="primary"
                variant="flat"
                @click="search({ lgbt: true })"
              >
                See More
              </v-btn>
            </v-window-item>
            <v-window-item :value="2">
              <ac-load-section :controller="communitySubmissions">
                <template #default>
                  <v-row dense>
                    <v-col
                      v-for="submission in communitySubmissionsList"
                      :key="submission.x!.id"
                      cols="6"
                      sm="4"
                      md="3"
                      lg="2"
                    >
                      <ac-gallery-preview
                        :submission="submission.x"
                        :show-footer="false"
                      />
                    </v-col>
                  </v-row>
                </template>
                <template #loading-spinner>
                  <v-row dense>
                    <v-col
                      v-for="i in Array(listSizer(true)).keys()"
                      :key="i"
                      cols="6"
                      sm="4"
                      md="3"
                      lg="2"
                    >
                      <v-responsive
                        aspect-ratio="1"
                        max-height="100%"
                        max-width="100%"
                      >
                        <v-skeleton-loader max-height="100%" type="image" />
                      </v-responsive>
                    </v-col>
                  </v-row>
                </template>
              </ac-load-section>
            </v-window-item>
          </v-window>
        </v-col>
        <v-col
          cols="12"
          md="12"
          :lg="isRegistered ? 6 : 12"
          class="px-1 py-2"
          :order="isRegistered ? 4 : 6"
        >
          <v-card :color="theme.current.value.colors['well-darken-4']">
            <v-toolbar dense color="secondary">
              <v-toolbar-title>Recent Submissions</v-toolbar-title>
              <v-spacer />
              <v-toolbar-items>
                <v-btn
                  color="primary"
                  class="search-submissions"
                  variant="flat"
                  @click="searchSubmissions({})"
                >
                  See More
                </v-btn>
              </v-toolbar-items>
            </v-toolbar>
            <v-card-text>Art uploaded by our users</v-card-text>
            <ac-load-section :controller="submissions">
              <template #default>
                <v-row dense>
                  <v-col
                    v-for="submission in submissionsList"
                    :key="submission.x!.id"
                    cols="6"
                    sm="4"
                    md="3"
                    :lg="isRegistered ? 4 : 2"
                  >
                    <ac-gallery-preview
                      :submission="submission.x"
                      :show-footer="false"
                    />
                  </v-col>
                </v-row>
              </template>
              <template #loading-spinner>
                <v-row dense>
                  <v-col
                    v-for="i in Array(listSizer(display.md.value)).keys()"
                    :key="i"
                    cols="6"
                    sm="4"
                    md="3"
                    lg="4"
                  >
                    <v-responsive
                      aspect-ratio="1"
                      max-height="100%"
                      max-width="100%"
                    >
                      <v-skeleton-loader max-height="100%" type="image" />
                    </v-responsive>
                  </v-col>
                </v-row>
              </template>
            </ac-load-section>
          </v-card>
        </v-col>
        <v-col cols="12" class="px-1 py-2" order="7">
          <v-card :color="theme.current.value.colors['well-darken-4']">
            <v-toolbar dense color="secondary">
              <v-toolbar-title>New Characters</v-toolbar-title>
              <v-spacer />
              <v-toolbar-items>
                <v-btn
                  color="primary"
                  class="search-characters"
                  variant="flat"
                  @click.stop="searchCharacters()"
                >
                  See More
                </v-btn>
              </v-toolbar-items>
            </v-toolbar>
            <v-card-text>Characters cataloged by our users</v-card-text>
            <ac-load-section :controller="characters">
              <template #default>
                <v-row dense>
                  <v-col
                    v-for="character in charactersList"
                    :key="character.x!.id"
                    cols="6"
                    sm="4"
                    md="3"
                    :lg="isRegistered ? 2 : 4"
                  >
                    <ac-character-preview
                      :character="character.x"
                      :show-footer="false"
                    />
                  </v-col>
                </v-row>
              </template>
              <template #loading-spinner>
                <v-row dense>
                  <v-col
                    v-for="i in Array(listSizer(true)).keys()"
                    :key="i"
                    cols="6"
                    sm="4"
                    md="3"
                    :lg="isRegistered ? 2 : 4"
                  >
                    <v-responsive
                      aspect-ratio="1"
                      max-height="100%"
                      max-width="100%"
                    >
                      <v-skeleton-loader max-height="100%" type="image" />
                    </v-responsive>
                  </v-col>
                </v-row>
              </template>
            </ac-load-section>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script setup lang="ts">
import { useViewer } from "@/mixins/viewer.ts"
import { ListController } from "@/store/lists/controller.ts"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcGalleryPreview from "@/components/AcGalleryPreview.vue"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import AcCharacterPreview from "@/components/AcCharacterPreview.vue"
import { makeQueryParams, shuffle, BASE_URL } from "@/lib/lib.ts"
import AcTabs from "@/components/navigation/AcTabs.vue"
import AcLink from "@/components/wrappers/AcLink.vue"
import AcProductSlider from "@/components/AcProductSlider.vue"
import { useForm } from "@/store/forms/hooks.ts"
import { useList } from "@/store/lists/hooks.ts"
import { computed, ref } from "vue"
import { Ratings } from "@/types/enums/Ratings.ts"
import { RouteLocationRaw, useRouter } from "vue-router"
import { useDisplay, useTheme } from "vuetify"
import { usePrerendering } from "@/mixins/prerendering.ts"
import {
  mdiPalette,
  mdiShieldHalfFull,
  mdiMagnify,
  mdiStar,
  mdiEmoticonOutline,
  mdiTag,
  mdiDice5,
} from "@mdi/js"
import { useSingle } from "@/store/singles/hooks.ts"
import AcProductPreview from "@/components/AcProductPreview.vue"
import AcAvatar from "@/components/AcAvatar.vue"
import { profileLink } from "@/lib/otherFormatters.ts"
import type { Product, Submission } from "@/types/main"
import { User } from "@/store/profiles/types/main"
import { RawData } from "@/store/forms/types/main"

const searchForm = useForm("search")
const featured = useSingle<
  User & { products: Product[]; submissions: Submission[] }
>("featured", {
  endpoint: "/api/sales/random-top-seller/",
})
featured.get()

const slicedFeaturedSubmissions = computed(() => {
  if (!featured.x) {
    return []
  }
  return featured.x.submissions.slice(1)
})

const theme = useTheme()

const rated = useList<Product>("rated", {
  endpoint: "/api/sales/highly-rated/",
  params: { size: 6 },
})

const lowPriced = useList<Product>("lowPriced", {
  endpoint: "/api/sales/low-price/",
  params: { size: 6 },
})

const artistsOfColor = useList<Product>("artistsOfColor", {
  endpoint: "/api/sales/artists-of-color/",
  params: { size: 6 },
})

const randomProducts = useList<Product>("randomProducts", {
  endpoint: "/api/sales/random/",
  params: { size: 6 },
})

const lgbt = useList<Product>("lgbt", {
  endpoint: "/api/sales/lgbt/",
  params: { size: 6 },
})

const commissions = useList<Submission>("commissions", {
  endpoint: "/api/profiles/recent-commissions/",
  params: { size: 6 },
})
commissions.firstRun()

const submissions = useList<Submission>("submissions", {
  endpoint: "/api/profiles/recent-submissions/",
  params: { size: 6 },
})
submissions.firstRun()

const communitySubmissions = useList<Submission>("communitySubmissions", {
  endpoint: "/api/profiles/community-submissions/",
  params: { size: 6 },
})
communitySubmissions.firstRun()

const characters = useList("newCharacters", {
  endpoint: "/api/profiles/new-characters/",
  params: { size: 6 },
})
characters.firstRun()

const { rating, isRegistered } = useViewer()
const router = useRouter()
const display = useDisplay()

const blogEntries = [
  {
    link: "https://artconomy.com/blog/pricing-your-artwork/",
    title: "7 Tips on Pricing your Artwork",
    image:
      "https://artconomy.com/blog/wp-content/uploads/2020/04/alvaro-reyes-MEldcHumbu8-unsplash.jpg",
  },
  {
    link: "https://artconomy.com/blog/tips-for-growing-your-audience/",
    title: "5 Tips for Growing your Audience as an Artist",
    image: "https://artconomy.com/blog/wp-content/uploads/2020/01/dragon.jpg",
  },
  {
    link: "https://artconomy.com/blog/posts/2019/07/31/5-tips-for-character-design/",
    title: "5 Tips for Character Design",
    image: "https://artconomy.com/blog/wp-content/uploads/2019/07/pirate.jpg",
  },
  {
    link: "https://artconomy.com/blog/selling-art-commissions/",
    title: "5 Ways to Protect Yourself When Selling Art Commissions",
    image:
      "https://artconomy.com/blog/wp-content/uploads/2019/05/piggybank.jpg",
  },
  {
    link: "https://artconomy.com/blog/making-art-your-side-hustle/",
    title: "7 Tips on Making Art your Side Hustle",
    image:
      "https://artconomy.com/blog/wp-content/uploads/2018/01/cover-web.jpeg",
  },
  {
    link: "https://artconomy.com/blog/what-you-need-to-an-artist/",
    title: "How to Describe What you Need to an Artist",
    image:
      "https://artconomy.com/blog/wp-content/uploads/2019/06/wrong-question.png",
  },
  {
    link: "https://artconomy.com/blog/escrow-for-art-commissions/",
    title: "Escrow For Art Commissions: 5 Reasons we use it",
    image:
      "https://artconomy.com/blog/wp-content/uploads/2022/11/defending-1885x2048.png",
  },
  {
    link: "https://artconomy.com/blog/art-commissions/",
    title: "5 Things to Know about Art Commissions",
    image:
      "https://artconomy.com/blog/wp-content/uploads/2020/11/kelly-sikkema-o2TRWThve_I-unsplash.jpg",
  },
]

const nsfwBlogEntries = [
  {
    link: "https://artconomy.com/blog/nsfw-commissions-tips-for-buyers/",
    title: "NSFW Commissions: 5 Tips for Buyers",
    image:
      "https://artconomy.com/blog/wp-content/uploads/2020/08/halcy0n-phoex-JasAra02-1536x1075.png",
  },
  {
    link: "https://artconomy.com/blog/nsfw-furry-artists/",
    title: "NSFW Furry Artists: 4 Tips to Find the Right One for You!",
    image:
      "https://artconomy.com/blog/wp-content/uploads/2022/08/blog1transparent-3.png",
  },
]

const banners = [
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-A1-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-A2-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-A3-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-A4-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-B1-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-B2-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-B3-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-B4-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-C1-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-C2-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-C3-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-C4-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-D1-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-D2-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-D3-1440x200.png",
      BASE_URL,
    ),
  },
  {
    artist: "Halcyon",
    src: new URL(
      "/static/images/halcy0n-artconomy-banner-D4-1440x200.png",
      BASE_URL,
    ),
  },
]

const articles = computed(() => {
  const sourceArticles = [...blogEntries]
  if (rating.value >= Ratings.ADULT) {
    // Remove some clean articles at random to make the NSFW articles more probable, since there
    // are far less of them.
    for (let i = 0; i < nsfwBlogEntries.length * 2; i++) {
      sourceArticles.splice(
        Math.floor(Math.random() * sourceArticles.length),
        1,
      )
    }
    sourceArticles.push(...nsfwBlogEntries)
  }
  const articles = shuffle(sourceArticles)
  return articles.slice(0, 2)
})

const searchTerms = shuffle(["refsheet", "ych", "stickers", "badge"]).slice(
  0,
  3,
)

const laptop = new URL("/static/images/laptop.png", BASE_URL).href
const fridge = new URL("/static/images/fridge.png", BASE_URL).href
const fingerPainting = new URL("/static/images/fingerpainting.png", BASE_URL)
  .href
const discord = new URL("/static/images/Discord.png", BASE_URL).href

const mainSectionItems = [
  {
    value: 0,
    title: "Featured",
    icon: mdiStar,
  },
  {
    value: 1,
    title: "Highly Rated",
    icon: mdiEmoticonOutline,
  },
  {
    value: 2,
    title: "Special Deals",
    icon: mdiTag,
  },
  {
    value: 3,
    title: "Random",
    icon: mdiDice5,
  },
]

const mainSection = ref(0)

const communityItems = [
  {
    value: 0,
    title: "Artists of Color",
  },
  {
    value: 1,
    title: "LGBTQ+",
  },
  {
    value: 2,
    title: "Artconomy",
  },
]

const communitySection = ref(shuffle([0, 1, 2])[0])

const searchReplace = (data: RawData) => {
  searchForm.reset()
  for (const key of Object.keys(data)) {
    searchForm.fields[key].update(data[key])
  }
}

const search = (data: RawData) => {
  searchReplace(data)
  router.push({
    name: "SearchProducts",
    query: makeQueryParams(searchForm.rawData),
  })
}

const searchFromField = () => {
  router.push({
    name: "SearchProducts",
    query: makeQueryParams(searchForm.rawData),
  })
}

const searchCharacters = () => {
  searchReplace({})
  router.push({
    name: "SearchCharacters",
    query: makeQueryParams(searchForm.rawData),
  })
}

const searchSubmissions = (data: RawData) => {
  searchReplace(data)
  router.push({
    name: "SearchSubmissions",
    query: makeQueryParams(searchForm.rawData),
  })
}

const listSizer = (long?: boolean) => {
  /* istanbul ignore if */
  if (display.xs.value) {
    return 2
  }
  /* istanbul ignore if */
  if (display.md.value && long) {
    return 4
  }
  /* istanbul ignore if */
  if (display.lgAndUp.value) {
    return 6
  }
  /* istanbul ignore if */
  return 3
}

const listPreview = (list: ListController<any>, long?: boolean) => {
  // Gives a few items from the list depending on screen size. Useful for things like the home page where we have many
  // sections to display at once, but don't want to crowd the screen too much.
  /* istanbul ignore if */
  return list.list.slice(0, listSizer(long))
}

const commissionsList = computed(() => listPreview(commissions, true))

const submissionsList = computed(() =>
  listPreview(submissions, display.md.value),
)

const communitySubmissionsList = computed(() =>
  listPreview(communitySubmissions),
)

const charactersList = computed(() => listPreview(characters, true))

const featuredOrder = computed(() => (isRegistered.value ? 2 : 1))

const randomBanner = banners[Math.floor(Math.random() * banners.length)]

const { prerendering } = usePrerendering()
</script>

<style scoped>
.credit-overlay {
  margin-top: -1.5rem;
  position: relative;
  z-index: 1;
  text-shadow: -1px -2px 3px black;
}
</style>
