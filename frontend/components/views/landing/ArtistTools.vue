<template>
  <v-container fluid>
    <v-row class="justify-content fill-height"  align="center">
      <v-col cols="12" md="6" class="text-center" order="1" order-md="1">
        <h2>List all of your products</h2>
        <p>With samples, commission info, and tags on a beautiful, mobile-ready site.</p>
        <v-btn large color="green" :to="url" :block="block" class="commission-cta"><v-icon left>store</v-icon>Open Your Store!</v-btn>
      </v-col>
      <v-col cols="12" md="6" order="2" order-md="2" class="pa-2">
        <v-img src="/static/images/marketing/product-detail.jpg" :elevation="14" :aspect-ratio="1357/565" />
      </v-col>
      <v-col cols="12" md="6" class="pa-2" order="4" order-md="3">
        <v-img src="/static/images/marketing/AWOO.jpg" :elevation="14" :aspect-ratio="1591/844" />
      </v-col>
      <v-col cols="12" md="6" lg="4" offset-lg="1" class="text-center" order="3" order-md="4">
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
        <v-btn large color="green" :to="url" :block="block" class="commission-cta"><v-icon left>assignment</v-icon>Get Organized</v-btn>
      </v-col>
      <v-col cols="12" md="6" class="text-center pa-2" order="7" order-lg="7">
        <v-img src="/static/images/marketing/discord-channel-log.jpg" :elevation="14" :aspect-ratio="1591/844" />
      </v-col>
      <v-col cols="12" md="6" class="text-center pa-2" order="6" order-lg="6">
        <h2>A Community-- You are not alone.</h2>
        <p>The artistic journey is one of persistence, and it can't be done alone.
          Engage with a community of artists from different walks of life, at any level of their career.</p>
        <p>Trade tips with a group of people eager to help each other succeed.</p>
        <p>Join our Discord channel, and get solid advice from the Artconomy ArtSmarts blog!</p>
        <v-row>
          <v-col cols="12" lg="6">
            <v-btn
              large
              v-if="!prerendering"
              href="https://discord.gg/4nWK9mf"
              target="_blank"
              :block="block"
              color="primary"><v-icon left>{{discordPath}}</v-icon>
              Join our Discord
            </v-btn>
            <v-btn v-else
                large
                :block="block"
                color="primary"><v-icon left>{{discordPath}}</v-icon>
                Join our Discord
            </v-btn>
          </v-col>
          <v-col cols="12" lg="6">
            <v-btn
              large
              color="secondary"
              href="https://artconomy.com/blog/"
              target="_blank"
              :block="block"
            ><v-icon left>palette</v-icon>Get ArtSmarts</v-btn>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12" md="6" lg="4" offset-lg="1" class="text-center pa-2" order="9">
        <h2>Flexible, helpful tools</h2>
        <p>Communicate directly with your customer, directly on each revision. Set how many revisions are included up front.</p>
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
      </v-col>
      <v-col cols="12" md="6" class="text-center pa-2" order="8">
        <v-img src="/static/images/marketing/pricing.jpg" :aspect-ratio="2356/1018" contain></v-img>
      </v-col>
    </v-row>
    <v-row class="justify-content fill-height" align="center">
      <v-col cols="12">
        <hr />
      </v-col>
      <v-col cols="12" md="6" offset-md="3" lg="4" offset-lg="4" class="text-center pa-2">
        <h1>Never get scammed</h1>
        <v-img src="/static/images/403.png" max-height="30vh" contain :aspect-ratio="1" />
        <p>With <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>, payment is guaranteed, and deposited right into your bank account.</p>
        <v-icon color="green">fa-shield</v-icon>
        <p><small>Artconomy shield currently only available to those with US Bank accounts.
          You can still handle orders through Artconomy if you do not have one, but will have to take payment from an outside source.</small></p>
        <v-btn large color="green" :to="url" :block="block" class="commission-cta"><v-icon left>lock</v-icon>Get Protected</v-btn>
      </v-col>
      <v-col cols="12">
        <hr />
      </v-col>
    </v-row>
    <v-row class="justify-content fill-height" align="center">
      <v-col cols="12" md="6" lg="4" class="text-center pa-2" order="2" order-lg="1">
        <v-img src="/static/images/marketing/references.jpg" contain :aspect-ratio="1613/607" />
      </v-col>
      <v-col cols="12" lg="4" class="text-center pa-5" order="1" order-lg="2">
        <h2>Keep Track of All of your References</h2>
        <p>Great, you have an order. Now where did you put that reference? Wonder no longer!
          Every order comes with reference management, allowing customers to upload what you need.</p>
        <p><strong>Character Listings</strong> allow you to keep track of your creations, or get a full view of your customer's OC!</p>
      </v-col>
      <v-col cols="12" md="6" lg="4" class="text-center pa-2" order="3" order-lg="3">
        <v-img src="/static/images/marketing/character.jpg" contain :aspect-ratio="2334/978" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" class="text-center">
        <h1>Ready?</h1>
        <p>Let's be better with help from each other!</p>
        <v-btn large color="green" :to="url" :block="block" class="commission-cta"><v-icon left>edit</v-icon>Get started!</v-btn>
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
import Component, {mixins} from 'vue-class-component'
import {mdiDiscord} from '@mdi/js'
import PrerenderMixin from '@/mixins/PrerenderMixin'
import Viewer from '@/mixins/viewer'

@Component
export default class ArtistTools extends mixins(PrerenderMixin, Viewer) {
  public discordPath = mdiDiscord
  public get url() {
    if (this.isRegistered) {
      return {name: 'Profile', params: {username: this.viewerName}}
    }
    return {name: 'Login', params: {tabName: 'register'}, query: {artist_mode: 'true'}}
  }

  public get block() {
    return this.$vuetify.breakpoint.xsOnly
  }
}
</script>
