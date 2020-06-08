<template>
  <v-container fluid class="pa-0">
    <v-container>
      <v-row no-gutters  >
        <v-col class="text-center px-2" cols="12" >
          <h1>Your ideas. <br class="hidden-sm-and-up" /> Your characters. Realized.</h1>
        </v-col>
        <v-col cols="8" offset="2" lg="4" offset-lg="4">
          <ac-bound-field
            :field="searchForm.fields.q"
            @keyup="$router.push({name: 'SearchProducts'})"
            label="I'm looking for..."
          />
        </v-col>
        <v-col class="text-center" cols="12" lg="6" offset-lg="3" >
          Try terms like:
          <v-chip color="secondary" @click="search({q: term})" class="mx-1" v-for="term in searchTerms" :key="term">{{term}}</v-chip>
        </v-col>
        <v-col class="text-center pt-3" cols="12" lg="6" offset-lg="3">
          <v-btn color="primary" @click="search({})">Browse Everyone Open</v-btn>
        </v-col>
      </v-row>
      <v-row no-gutters class="pt-2">
        <v-col class="text-center d-flex" cols="12" md="4" >
          <v-row no-gutters >
            <v-col class="grow pa-1" >
              <v-row no-gutters>
                <v-col cols="6" md="12" order="2" order-md="1">
                  <v-img src="/static/images/laptop.png" max-height="20vh" contain />
                </v-col>
                <v-col cols="6" md="12" order="1" order-md="2">
                  <v-row no-gutters class="justify-content fill-height"  align="center" >
                    <v-col class="pa-1" >
                      Find an artist you want to commission, and place an order describing what you want.
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
            <v-col class="hidden-sm-and-down shrink">
              <v-divider vertical />
            </v-col>
          </v-row>
        </v-col>
        <v-col class="text-center d-flex" cols="12" md="4" >
          <v-row no-gutters >
            <v-col class="grow pa-1" >
              <v-row no-gutters  >
                <v-col cols="6" md="12">
                  <v-img src="/static/images/fingerpainting.png" max-height="20vh" contain />
                </v-col>
                <v-col class="pa-1" cols="6" md="12" >
                  <v-row no-gutters class="justify-content fill-height"  align="center" >
                    <v-col>
                      <p>We hold onto your payment until the work is done. In the event the artist fails to complete the assignment, you'll get your money back!*</p>
                      <p><small>* Protection available only on
                        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>
                        <v-icon color="green" class="px-1">fa-shield</v-icon>
                        enabled products.</small></p>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
            <v-col class="hidden-sm-and-down shrink">
              <v-divider vertical />
            </v-col>
          </v-row>
        </v-col>
        <v-col class="text-center d-flex" cols="12" md="4" >
          <v-row no-gutters >
            <v-col class="grow pa-1" >
              <v-row dense>
                <v-col cols="6" md="12" order="2" order-md="1">
                  <v-img src="/static/images/fridge.png" max-height="20vh" contain />
                </v-col>
                <v-col cols="6" md="12" order="1" order-md="2">
                  <v-row class="justify-content fill-height"  align="center" >
                    <v-col>
                      Once completed, you can catalog and show off your completed piece to the world! If you have a character, you can add it to your character's gallery, too!
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
    <v-container fluid>
      <ac-tabs :items="mainSectionItems" v-model="mainSection" />
      <v-tabs-items :value="mainSection">
        <v-tab-item>
          <v-card-text>High quality products by artists who have been vetted by our team.</v-card-text>
          <v-carousel height="420" :show-arrows="true" v-model="featuredSlider" :continuous="true" :hide-delimiters="true">
            <v-carousel-item v-for="product in featuredList" :key="product.x.id">
              <ac-product-preview :carousel="true" :product="product.x" />
            </v-carousel-item>
          </v-carousel>
          <v-btn block color="primary" @click="search({featured: true})">See All Featured</v-btn>
        </v-tab-item>
        <v-tab-item>
          <v-card-text>Products by artists given high ratings by previous commissioners</v-card-text>
          <v-carousel height="420" :show-arrows="true" v-model="ratedSlider" :continuous="true" :cycle="true" :hide-delimiters="true">
            <v-carousel-item v-for="product in rated.list" :key="product.x.id">
              <ac-product-preview :carousel="true" :product="product.x" />
            </v-carousel-item>
          </v-carousel>
          <v-btn block color="primary" @click="search({rating: true})">See More</v-btn>
        </v-tab-item>
        <v-tab-item>
          <v-card-text>Looking for something lower-budget? Check out these offerings from our artists, $30 or less!</v-card-text>
          <v-carousel height="420" :show-arrows="true" v-model="dealSlider" :continuous="true" :cycle="true" :hide-delimiters="true">
            <v-carousel-item v-for="product in lowPriced.list" :key="product.x.id">
              <ac-product-preview :carousel="true" :product="product.x" />
            </v-carousel-item>
          </v-carousel>
          <v-btn block color="primary" @click="search({max_price: '30.00'})" class="low-price-more">See More</v-btn>
        </v-tab-item>
        <v-tab-item>
          <v-card-text>Feeling lucky? Here are some offers from our artists at random!</v-card-text>
          <v-carousel height="420" :show-arrows="true" v-model="randomSlider" :continuous="true" :cycle="true" :hide-delimiters="true">
            <v-carousel-item v-for="product in randomProducts.list" :key="product.x.id">
              <ac-product-preview :carousel="true" :product="product.x" />
            </v-carousel-item>
          </v-carousel>
          <v-btn color="primary" @click="search({})" block>Browse Everyone Open</v-btn>
        </v-tab-item>
      </v-tabs-items>
      <v-row no-gutters class="pt-3">
        <v-col cols="12" md="6" class="pa-1">
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
            <v-toolbar dense color="secondary">
              <v-toolbar-title>Recent Commissions</v-toolbar-title>
            </v-toolbar>
            <v-card-text>Commissions recently completed by our artists</v-card-text>
            <ac-load-section :controller="commissions">
              <template v-slot:default>
                <v-row dense>
                  <v-col cols="6" sm="4" v-for="submission in commissionsList" :key="submission.id">
                    <ac-gallery-preview :submission="submission.x" :mini="true" />
                  </v-col>
                </v-row>
              </template>
            </ac-load-section>
          </v-card>
        </v-col>
        <v-col cols="12" md="6" class="pa-1">
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
            <v-toolbar dense color="secondary">
              <v-toolbar-title>Community Resources</v-toolbar-title>
            </v-toolbar>
          <v-row>
            <v-col cols="6" class="text-center" v-if="!prerendering" align-self="center">
              <v-img src="/static/images/Discord.png"></v-img>
            </v-col>
            <v-col cols="6" class="text-center" align-self="center">
              <p><strong>Want your voice to be heard, to network with artists, and meet new friends?</strong></p>
              <p>Check out our Discord!</p>
              <v-btn
                href="https://discord.gg/4nWK9mf"
                target="_blank"
                rel="nofollow,noopener"
                color="primary"
                v-if="!prerendering"
              >
                Join now!
              </v-btn>
              <v-btn v-else color="primary">
                Join now!
              </v-btn>
            </v-col>
            <v-col cols="6" align-self="center">
              <v-col class="text-center">
                <v-img :src="articles[0].image" alt=""></v-img>
              </v-col>
              <v-col class="text-center">
                <strong>
                  <a :href="articles[0].link" target="_blank">{{articles[0].title}}</a>
                </strong>
              </v-col>
            </v-col>
            <v-col cols="6" align-self="center">
              <v-col class="text-center">
                <v-img :src="articles[1].image" alt=""></v-img>
              </v-col>
              <v-col class="text-center">
                <strong>
                  <a :href="articles[1].link" target="_blank">{{articles[1].title}}</a>
                </strong>
              </v-col>
            </v-col>
          </v-row>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-if="showCommunities">
        <v-col class="text-center">
          <v-card color="secondary">
            <v-card-text class="text-center">
              <h2>Find Your Community</h2>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <ac-tabs :items="communityItems" v-model="communitySection" v-if="showCommunities" />
      <v-tabs-items :value="communitySection" v-if="showCommunities">
        <v-tab-item v-if="artistsOfColor.list.length">
          <v-carousel height="420" :show-arrows="true" v-model="artistsOfColorSlider" :continuous="true" :hide-delimiters="true">
            <v-carousel-item v-for="product in artistsOfColor.list" :key="product.x.id">
              <ac-product-preview :carousel="true" :product="product.x" />
            </v-carousel-item>
          </v-carousel>
          <v-btn block color="primary" @click="search({featured: true})">See More</v-btn>
        </v-tab-item>
        <v-tab-item v-if="lgbt.list.length">
          <v-carousel height="420" :show-arrows="true" v-model="lgbtSlider" :continuous="true" :hide-delimiters="true">
            <v-carousel-item v-for="product in lgbt.list" :key="product.x.id">
              <ac-product-preview :carousel="true" :product="product.x" />
            </v-carousel-item>
          </v-carousel>
          <v-btn block color="primary" @click="search({featured: true})">See More</v-btn>
        </v-tab-item>
      </v-tabs-items>
      <v-row no-gutters>
        <v-col cols="12" md="6" class="pa-1">
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
            <v-toolbar dense color="secondary">
              <v-toolbar-title>Recent Submissions</v-toolbar-title>
              <v-spacer />
              <v-toolbar-items>
                <v-btn color="primary" @click="searchSubmissions()" class="search-submissions">See More</v-btn>
              </v-toolbar-items>
            </v-toolbar>
            <v-card-text>Art uploaded by our users</v-card-text>
            <ac-load-section :controller="submissions">
              <template v-slot:default>
                <v-row dense>
                  <v-col cols="6" sm="4" v-for="submission in submissionsList" :key="submission.id">
                    <ac-gallery-preview :submission="submission.x" :mini="true" />
                  </v-col>
                </v-row>
              </template>
            </ac-load-section>
          </v-card>
        </v-col>
        <v-col cols="12" md="6" class="pa-1">
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
            <v-toolbar dense color="secondary">
              <v-toolbar-title>New Characters</v-toolbar-title>
              <v-spacer />
              <v-toolbar-items>
                <v-btn color="primary" @click.stop="searchCharacters()" class="search-characters">See More</v-btn>
              </v-toolbar-items>
            </v-toolbar>
            <v-card-text>Characters catalogged by our users</v-card-text>
            <ac-load-section :controller="characters">
              <template v-slot:default>
                <v-row dense>
                  <v-col cols="6" sm="4" v-for="character in charactersList" :key="character.id">
                    <ac-character-preview :character="character.x" :mini="true" />
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

<script lang="ts">

import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {FormController} from '@/store/forms/form-controller'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import Submission from '@/types/Submission'
import {RawData} from '@/store/forms/types/RawData'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import {Character} from '@/store/characters/types/Character'
import {shuffle} from '@/lib/lib'
import AcTabs from '@/components/navigation/AcTabs.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAsset from '@/components/AcAsset.vue'
import Formatting from '@/mixins/formatting'
import AcRendered from '@/components/wrappers/AcRendered'
import AcAvatar from '@/components/AcAvatar.vue'
import {mdiDiscord} from '@mdi/js'
import PrerenderMixin from '@/mixins/PrerenderMixin'

@Component({
  components: {
    AcAvatar,
    AcRendered,
    AcAsset,
    AcLink,
    AcTabs,
    AcCharacterPreview,
    AcGalleryPreview,
    AcBoundField,
    AcLoadSection,
    AcProductPreview,
  },
})
export default class Home extends mixins(Viewer, Formatting, PrerenderMixin) {
    public searchForm: FormController = null as unknown as FormController
    public featured: ListController<Product> = null as unknown as ListController<Product>
    public rated: ListController<Product> = null as unknown as ListController<Product>
    public newArtistProducts: ListController<Product> = null as unknown as ListController<Product>
    public randomProducts: ListController<Product> = null as unknown as ListController<Product>
    public lowPriced: ListController<Product> = null as unknown as ListController<Product>
    public commissions: ListController<Submission> = null as unknown as ListController<Submission>
    public submissions: ListController<Submission> = null as unknown as ListController<Submission>
    public characters: ListController<Character> = null as unknown as ListController<Character>
    public lgbt: ListController<Product> = null as unknown as ListController<Product>
    public artistsOfColor: ListController<Product> = null as unknown as ListController<Product>
    public mainSection = 0
    public featuredSlider = 0
    public randomSlider = 0
    public ratedSlider = 0
    public dealSlider = 0
    public communitySection = 0
    public artistsOfColorSlider = 0
    public lgbtSlider = 0
    public discordPath = mdiDiscord
    public banners = [
      {file: 'halcy0n-artconomy-banner-A1-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-A2-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-A3-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-A4-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-B1-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-B2-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-B3-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-B4-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-C1-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-C2-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-C3-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-C4-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-D1-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-D2-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-D3-1440x200.png', username: 'Halcyon'},
      {file: 'halcy0n-artconomy-banner-D4-1440x200.png', username: 'Halcyon'},
    ]
    public blogEntries = [
      {
        link: 'https://artconomy.com/blog/posts/2020/04/29/7-tips-on-pricing-your-artwork/',
        title: '7 Tips on Pricing your Artwork',
        image: 'https://artconomy.com/blog/wp-content/uploads/2020/04/alvaro-reyes-MEldcHumbu8-unsplash.jpg',
      },
      {
        link: 'https://artconomy.com/blog/posts/2020/01/13/5-tips-for-growing-your-audience-as-an-artist/',
        title: '5 Tips for Growing your Audience as an Artist',
        image: 'https://artconomy.com/blog/wp-content/uploads/2020/01/dragon.jpg',
      },
      {
        link: 'https://artconomy.com/blog/posts/2019/07/31/5-tips-for-character-design/',
        title: '5 Tips for Character Design',
        image: 'https://artconomy.com/blog/wp-content/uploads/2019/07/pirate.jpg',
      },
      {
        link: 'https://artconomy.com/blog/posts/2019/05/17/staying-safe-how-to-prevent-getting-scammed-when-selling-commissions/',
        title: '5 Ways to Protect Yourself When Selling Art Commissions',
        image: 'https://artconomy.com/blog/wp-content/uploads/2019/05/piggybank.jpg',
        width: 100,
        height: 100,
      },
      {
        link: 'https://artconomy.com/blog/posts/2019/05/01/the-transition-process-making-art-your-side-hustle/',
        title: '7 Tips on Making Art your Side Hustle',
        image: 'https://artconomy.com/blog/wp-content/uploads/2018/01/cover-web.jpeg',
      },
      {
        link: 'https://artconomy.com/blog/posts/2018/11/15/how-to-describe-what-you-need-to-an-artist/',
        title: 'How to Describe What you Need to an Artist',
        image: 'https://artconomy.com/blog/wp-content/uploads/2019/06/wrong-question.png',
      },
    ]
    public get randomBanner() {
      // Lazy calculation, so should always match on a specific render.
      return shuffle(this.banners)[0]
    }

    public get articles() {
      const articles = shuffle(this.blogEntries)
      return articles.slice(0, 2)
    }

    public get searchTerms() {
      return shuffle(['refsheet', 'ych', 'stickers', 'badge']).slice(0, 3)
    }

    public get showCommunities() {
      return (this.lgbt.list.length || this.artistsOfColor.list.length)
    }

    public get mainSectionItems() {
      return [
        {value: 0, text: 'Featured', icon: 'star'},
        {value: 1, text: 'Highly Rated', icon: 'mood'},
        {value: 2, text: 'Special Deals', icon: 'local_offer'},
        {value: 3, text: 'Random', icon: 'casino'},
      ]
    }

    public get communityItems() {
      const items = []
      if (this.artistsOfColor.list.length) {
        items.push({value: 0, text: 'Artists of Color', icon: ''})
      }
      if (this.lgbt.list.length) {
        items.push({value: 1, text: 'LGBTQ+', icon: ''})
      }
      return items
    }

    public searchReplace(data: RawData) {
      this.searchForm.reset()
      for (const key of Object.keys(data)) {
        this.searchForm.fields[key].update(data[key])
      }
    }

    public search(data: RawData) {
      this.searchReplace(data)
      this.$router.push({name: 'SearchProducts', query: data})
    }

    public searchCharacters() {
      this.searchReplace({})
      this.$router.push({name: 'SearchCharacters'})
    }

    public searchSubmissions() {
      this.searchReplace({})
      this.$router.push({name: 'SearchSubmissions'})
    }

    public listPreview(list: ListController<any>) {
      // Gives a few items from the list depending on screen size. Useful for things like the home page where we have many
      // sections to display at once, but don't want to crowd the screen too much.
      /* istanbul ignore if */
      if (this.$vuetify.breakpoint.xsOnly) {
        return list.list.slice(0, 2)
      }
      /* istanbul ignore if */
      if (this.$vuetify.breakpoint.lgAndUp) {
        return list.list.slice(0, 6)
      }
      /* istanbul ignore if */
      return list.list.slice(0, 3)
    }

    public get featuredList() {
      return this.listPreview(this.featured)
    }

    public get commissionsList() {
      return this.listPreview(this.commissions)
    }

    public get submissionsList() {
      return this.listPreview(this.submissions)
    }

    public get charactersList() {
      return this.listPreview(this.characters)
    }

    public created() {
      this.searchForm = this.$getForm('search')
      this.featured = this.$getList('featured', {endpoint: '/api/sales/v1/featured-products/', pageSize: 6})
      this.featured.firstRun()
      this.rated = this.$getList('rated', {endpoint: '/api/sales/v1/highly-rated/', pageSize: 6})
      this.rated.firstRun()
      this.lowPriced = this.$getList('lowPriced', {endpoint: '/api/sales/v1/low-price/', pageSize: 6})
      this.lowPriced.firstRun()
      this.newArtistProducts = this.$getList(
        'newArtistProducts', {endpoint: '/api/sales/v1/new-artist-products/', pageSize: 6}
      )
      this.lgbt = this.$getList(
        'lgbt', {endpoint: '/api/sales/v1/lgbt/', pageSize: 6}
      )
      this.artistsOfColor = this.$getList(
        'artistsOfColor', {endpoint: '/api/sales/v1/artists-of-color/', pageSize: 6}
      )
      this.randomProducts = this.$getList(
        'randomProducts', {endpoint: '/api/sales/v1/random/', pageSize: 6}
      )
      this.randomProducts.firstRun()
      this.newArtistProducts.firstRun()
      this.artistsOfColor.firstRun()
      this.lgbt.firstRun()
      this.commissions = this.$getList(
        'commissions', {endpoint: '/api/profiles/v1/recent-commissions/', pageSize: 6}
      )
      this.commissions.firstRun()
      this.submissions = this.$getList(
        'submissions', {endpoint: '/api/profiles/v1/recent-submissions/', pageSize: 6}
      )
      this.submissions.firstRun()
      this.characters = this.$getList('newCharacters', {endpoint: '/api/profiles/v1/new-characters/', pageSize: 6})
      this.characters.firstRun()
    }
}
</script>
