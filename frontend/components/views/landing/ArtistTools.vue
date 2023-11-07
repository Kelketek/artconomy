<template>
  <v-container fluid>
    <v-row class="justify-content fill-height" align="center">
      <v-col cols="12" md="6" lg="4" offset-lg="1" class="text-center" order="1" order-md="1">
        <h2>List all of your products</h2>
        <p>With samples, commission info, and tags on a beautiful, mobile-ready site.</p>
        <v-btn x-large color="green" :to="url" :block="block" variant="flat" class="commission-cta">
          <v-icon left icon="mdi-store"/>
          Open Your Store!
        </v-btn>
      </v-col>
      <v-col cols="12" md="6" order="2" order-md="2" class="pa-2" offset-lg="1">
        <v-img :src="productDetail" :elevation="14" :aspect-ratio="1357/565"/>
      </v-col>
      <v-col cols="12" md="6" class="pa-2" order="4" order-md="3">
        <v-img :src="awoo" :elevation="14" :aspect-ratio="1591/844"/>
      </v-col>
      <v-col cols="12" md="6" lg="4" offset-lg="1" class="text-center" order="3" order-md="4">
        <hr class="hidden-md-and-up"/>
        <div class="py-3 hidden-md-and-up"></div>
        <h2>Never say</h2>
        <p><s>"Note me if I owe you art"</s></p>
        <p>Meet <strong>AWOO</strong>, the
          <strong>A</strong>rtconomy
          <strong>W</strong>orkload
          <strong>O</strong>rganization and
          <strong>O</strong>verview tool.
          Find all of your orders, broadcast announcements to your commissioners.
        </p>
        <p>
          <strong>Never forget a task.</strong> Even if you took an order off Artconomy, <strong>AWOO</strong> invoices
          can still help you keep track of it, and in touch with your commissioner.
        </p>
        <v-btn x-large color="green" :to="url" :block="block" variant="flat" class="commission-cta">
          <v-icon left icon="mdi-assignment"/>
          Get Organized
        </v-btn>
      </v-col>
      <v-col cols="12" md="6" class="text-center pa-2" order="7" order-lg="7">
        <v-img :src="discordChannelLog" :elevation="14" :aspect-ratio="1591/844"/>
      </v-col>
      <v-col cols="12" md="6" class="text-center pa-2" order="6" order-lg="6">
        <hr class="hidden-md-and-up"/>
        <div class="py-3 hidden-md-and-up"></div>
        <h2>A Community-- You are not alone.</h2>
        <p>The artistic journey is one of persistence, and it can't be done alone.
          Engage with a community of artists from different walks of life, at any level of their career.</p>
        <p>Trade tips with a group of people eager to help each other succeed.</p>
        <p>Join our Discord channel, and get solid advice from the Artconomy ArtSmarts blog!</p>
        <v-row>
          <v-col cols="12" lg="6">
            <v-btn
                x-large
                href="https://discord.gg/4nWK9mf"
                target="_blank"
                :block="block"
                variant="flat"
                color="primary">
              <v-icon left icon="{{discordPath}}"/>
              Join our Discord
            </v-btn>
          </v-col>
          <v-col cols="12" lg="6">
            <v-btn
                x-large
                color="secondary"
                variant="flat"
                href="https://artconomy.com/blog/"
                target="_blank"
                :block="block"
            >
              <v-icon left icon="mdi-palette"/>
              Get ArtSmarts
            </v-btn>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12" md="6" lg="4" offset-lg="1" class="text-center pa-2" order="8" order-md="9">
        <hr class="hidden-md-and-up"/>
        <div class="py-3 hidden-md-and-up"></div>
        <h2>Flexible, helpful tools</h2>
        <p>Communicate directly with your customer, directly on each revision. Set how many revisions are included up
          front.</p>
        <p>Customer wants wings? Add a line item for it.
          Not sure how much you're making? Our calculator can help!</p>
        <v-card>
          <v-card-text color="blue">
            <strong>Keep track of references and characters on every commission!</strong>
          </v-card-text>
        </v-card>
        <p>
          Premade agreements, and little reminders to take care of yourself keep you on the path to running a
          stable businesses.
        </p>
        <v-btn x-large color="green" :to="url" :block="block" variant="flat" class="commission-cta">
          <v-icon left icon="mdi-construction"/>
          Equip Yourself!
        </v-btn>
      </v-col>
      <v-col cols="12" md="6" class="text-center pa-2" order="9" order-md="9">
        <v-img :src="pricing" :aspect-ratio="2356/1018" contain></v-img>
      </v-col>
    </v-row>
    <v-row class="justify-content fill-height" align="center">
      <v-col cols="12">
        <hr/>
      </v-col>
      <v-col cols="12" md="6" offset-md="3" lg="4" offset-lg="4" class="text-center pa-2">
        <h1>Never get scammed</h1>
        <v-img :src="forbidden" max-height="30vh" contain :aspect-ratio="1"/>
        <p>With
          <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>
          , payment is guaranteed, and deposited right into your bank account.
        </p>
        <v-icon color="green" icon="mdi-shield-half-full"/>
        <p><small>Artconomy shield currently available
          <router-link :to="{name: 'BuyAndSell', params: {question: 'bank-accounts'}}">in many countries</router-link>
          . However, some countries may not support shield.
          You can still handle orders through Artconomy if you are not in a supported country, but will have to take
          payment from an outside source.</small></p>
        <v-btn x-large color="green" :to="url" :block="block" variant="flat" class="commission-cta">
          <v-icon left icon="mdi-lock"/>
          Get Protected
        </v-btn>
      </v-col>
      <v-col cols="12">
        <hr/>
      </v-col>
    </v-row>
    <v-row class="justify-content fill-height" align="center">
      <v-col cols="12" md="6" lg="4" class="text-center pa-2" order="2" order-lg="1">
        <v-img :src="references" contain :aspect-ratio="1613/607"/>
      </v-col>
      <v-col cols="12" lg="4" class="text-center pa-5" order="1" order-lg="2">
        <h2>Keep Track of All of your References</h2>
        <p>Great, you have an order. Now where did you put that reference? Wonder no longer!
          Every order comes with reference management, allowing customers to upload what you need.</p>
        <p><strong>Character Listings</strong> allow you to keep track of your creations, or get a full view of your
          customer's OC!</p>
      </v-col>
      <v-col cols="12" md="6" lg="4" class="text-center pa-2" order="3" order-lg="3">
        <v-img :src="character" contain :aspect-ratio="2334/978"/>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="6" offset-md="3" lg="4" offset-lg="4" class="text-center">
        <hr class="hidden-md-and-up"/>
        <div class="py-3 hidden-md-and-up"></div>
        <h1>Ready?</h1>
        <p>Let's grow together!</p>
        <v-btn x-large color="green" :to="url" :block="block" variant="flat" class="commission-cta">
          <v-icon left icon="mdi-pencil"/>
          Get started!
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.hero-text {
  text-shadow: 2px 2px 5px #000000;
}
</style>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import {siDiscord} from 'simple-icons'
import Viewer from '@/mixins/viewer'
import {BASE_URL} from '@/lib/lib'

@Component({})
class ArtistTools extends mixins(Viewer) {
  public discordPath = siDiscord
  public character = new URL('/static/images/marketing/character.jpg', BASE_URL).href
  public references = new URL('/static/images/marketing/references.jpg', BASE_URL).href
  public forbidden = new URL('/static/images/403.png', BASE_URL).href
  public pricing = new URL('/static/images/marketing/pricing.jpg', BASE_URL).href
  public discordChannelLog = new URL('/static/images/marketing/discord-channel-log.jpg', BASE_URL).href
  public awoo = new URL('/static/images/marketing/AWOO.jpg', BASE_URL).href
  public productDetail = new URL('/static/images/marketing/product-detail.jpg', BASE_URL).href

  public get url() {
    if (this.isRegistered) {
      return {
        name: 'Profile',
        params: {username: this.viewerName},
      }
    }
    return {
      name: 'Register',
      query: {artist_mode: 'true'},
    }
  }

  public get block() {
    return true
    // return this.$vuetify.display.xs
  }
}

export default toNative(ArtistTools)
</script>
