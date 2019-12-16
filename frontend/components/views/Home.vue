<template>
  <v-container>
    <v-col>
      <v-img :src="`/static/images/${randomBanner.file}`" contain />
      <p class="px-1">Banner by <router-link :to="{name: 'Profile', params: {username: randomBanner.username}}">{{randomBanner.username}}</router-link></p>
    </v-col>
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
      <v-col class="text-center" cols="12" offset-sm="2" lg="6" offset-lg="3" >
        Try terms like:
        <v-chip color="secondary" @click="search({q: 'refsheet'})" class="mx-1">refsheet</v-chip>
          <v-chip color="secondary" @click="search({q: 'badge'})" class="mx-1">badge</v-chip>
          <v-chip color="secondary" @click="search({q: 'stickers'})" class="mx-1">stickers</v-chip>
          <v-chip color="secondary" @click="search({q: 'ych'})" class="mx-1">ych</v-chip>
      </v-col>
    </v-row>
    <v-row no-gutters   class="py-2">
      <v-col class="text-center d-flex" cols="12" md="4" >
        <v-row no-gutters >
          <v-col class="grow pa-1" >
            <v-row no-gutters  >
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
    <v-row no-gutters  >
      <v-col cols="12" md="6" class="pa-1">
        <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
          <v-toolbar dense color="secondary">
            <v-toolbar-title>Featured Offers</v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn color="primary" @click="search({featured: true})">See More</v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-card-text>High quality products by artists who have been vetted by our team.</v-card-text>
          <ac-load-section :controller="featured">\
            <template v-slot:default>
              <v-row dense>
                <v-col cols="6" sm="4" v-for="product in featuredList" :key="product.id">
                  <ac-product-preview :product="product.x" :mini="true" />
                </v-col>
              </v-row>
            </template>
          </ac-load-section>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" class="pa-1">
        <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
          <v-toolbar dense color="secondary">
            <v-toolbar-title>Highly Rated</v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn color="primary" @click="search({rating: true})">See More</v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-card-text>Products by artists given high ratings by previous commissioners</v-card-text>
          <ac-load-section :controller="rated">
            <template v-slot:default>
              <v-row dense>
                <v-col cols="6" sm="4" v-for="product in ratedList" :key="product.id">
                  <ac-product-preview :product="product.x" :mini="true" />
                </v-col>
              </v-row>
            </template>
          </ac-load-section>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" class="pa-1">
        <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
          <v-toolbar dense color="secondary">
            <v-toolbar-title>Special Deals</v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn color="primary" @click="search({max_price: '30.00'})" class="low-price-more">See More</v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-card-text>Looking for something lower-budget? Check out these offerings from our artists, $30 or less!</v-card-text>
          <ac-load-section :controller="lowPriced">
            <template v-slot:default>
              <v-row dense>
                <v-col cols="6" sm="4" v-for="product in lowPricedList" :key="product.id">
                  <ac-product-preview :product="product.x" :mini="true" />
                </v-col>
              </v-row>
            </template>
          </ac-load-section>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" class="pa-1">
        <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
          <v-toolbar dense color="secondary">
            <v-toolbar-title>New Artists</v-toolbar-title>
          </v-toolbar>
          <v-card-text>These artists have recently listed with Artconomy and you could be the first to commission them!</v-card-text>
          <ac-load-section :controller="newArtistProducts">
            <template v-slot:default>
              <v-row dense>
                <v-col cols="6" sm="4" v-for="product in newArtistProductsList" :key="product.id">
                  <ac-product-preview :product="product.x" :mini="true" />
                </v-col>
              </v-row>
            </template>
          </ac-load-section>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" class="pa-1">
        <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
          <v-toolbar dense color="secondary">
            <v-toolbar-title>Random Products</v-toolbar-title>
          </v-toolbar>
          <v-card-text>Feeling lucky? Here are some offers from our artists at random!</v-card-text>
          <ac-load-section :controller="randomProducts">
            <template v-slot:default>
              <v-row dense>
                <v-col cols="6" sm="4" v-for="product in randomProductsList" :key="product.id">
                  <ac-product-preview :product="product.x" :mini="true" />
                </v-col>
              </v-row>
            </template>
          </ac-load-section>
        </v-card>
      </v-col>
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
            <v-toolbar-title>Recent Submissions</v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn color="primary" :to="{name: 'SearchSubmissions'}">See More</v-btn>
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
              <v-btn color="primary" :to="{name: 'SearchCharacters'}">See More</v-btn>
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
</template>

<script lang="ts">

import Component, {mixins} from 'vue-class-component'
import Viewer from '../../mixins/viewer'
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
  @Component({
    components: {AcCharacterPreview, AcGalleryPreview, AcBoundField, AcLoadSection, AcProductPreview},
  })
export default class Home extends mixins(Viewer) {
    public searchForm: FormController = null as unknown as FormController
    public featured: ListController<Product> = null as unknown as ListController<Product>
    public rated: ListController<Product> = null as unknown as ListController<Product>
    public newArtistProducts: ListController<Product> = null as unknown as ListController<Product>
    public randomProducts: ListController<Product> = null as unknown as ListController<Product>
    public lowPriced: ListController<Product> = null as unknown as ListController<Product>
    public commissions: ListController<Submission> = null as unknown as ListController<Submission>
    public submissions: ListController<Submission> = null as unknown as ListController<Submission>
    public characters: ListController<Character> = null as unknown as ListController<Character>
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
    public get randomBanner() {
      // Lazy calculation, so should always match on a specific render.
      return this.banners[Math.floor(Math.random() * this.banners.length)]
    }

    public search(data: RawData) {
      this.searchForm.reset()
      for (const key of Object.keys(data)) {
        this.searchForm.fields[key].update(data[key])
      }
      this.$router.push({name: 'SearchProducts', query: data})
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

    public get ratedList() {
      return this.listPreview(this.rated)
    }

    public get lowPricedList() {
      return this.listPreview(this.lowPriced)
    }

    public get newArtistProductsList() {
      return this.listPreview(this.newArtistProducts)
    }

    public get randomProductsList() {
      return this.listPreview(this.randomProducts)
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
      this.randomProducts = this.$getList(
        'randomProducts', {endpoint: '/api/sales/v1/random/', pageSize: 6}
      )
      this.randomProducts.firstRun()
      this.newArtistProducts.firstRun()
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
