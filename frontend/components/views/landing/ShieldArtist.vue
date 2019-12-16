<template>
  <v-container fluid class="pa-0">
    <v-img src="/static/images/banner.jpg" :aspect-ratio="16/9" max-height="250px">
      <v-row no-gutters
        align="center"
        justify="center"
                class="hero-text fill-height"
      >
        <v-col>
          <h1 class="display-2 font-weight-thin mb-3">Always Get Paid</h1>
          <h2>Stay Organized Effortlessly</h2>
        </v-col>
      </v-row>
    </v-img>
    <v-container>
      <v-row no-gutters   class="py-2">
        <v-col class="text-center d-flex" cols="12" md="4" >
          <v-row no-gutters >
            <v-col class="grow pa-1" >
              <v-row no-gutters  >
                <v-col cols="6" md="12" order="2" order-md="1">
                  <v-img src="/static/images/laptop.png" max-height="20vh" contain></v-img>
                </v-col>
                <v-col cols="6" md="12" order="1" order-md="2">
                  <v-row no-gutters class="justify-content fill-height"  align="center" >
                    <v-col class="pa-1" >
                      Take orders through your store. You'll never lose track of your customer's contact information, or who you owe art, ever again!
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
            <v-col class="hidden-sm-and-down shrink">
              <v-divider vertical></v-divider>
            </v-col>
          </v-row>
        </v-col>
        <v-col class="text-center d-flex" cols="12" md="4" >
          <v-row no-gutters >
            <v-col class="grow pa-1" >
              <v-row no-gutters  >
                <v-col cols="6" md="12">
                  <v-img src="/static/images/403.png" max-height="20vh" contain></v-img>
                </v-col>
                <v-col class="pa-1" cols="6" md="12" >
                  <v-row no-gutters class="justify-content fill-height"  align="center" >
                    <v-col>
                      <p><strong>Never get scammed.</strong> With <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>, payment is guaranteed.</p>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
            <v-col class="hidden-sm-and-down shrink">
              <v-divider vertical></v-divider>
            </v-col>
          </v-row>
        </v-col>
        <v-col class="text-center d-flex" cols="12" md="4" >
          <v-row no-gutters >
            <v-col class="grow pa-1" >
              <v-row no-gutters  >
                <v-col cols="6" md="12" order="2" order-md="1">
                  <v-img src="/static/images/fridge.png" max-height="20vh" contain></v-img>
                </v-col>
                <v-col class="pa-1" cols="6" md="12" order="1" order-md="2">
                  <v-row no-gutters class="justify-content fill-height"  align="center" >
                    <v-col>
                      Tools built just for you: Galleries, Invoicing, Workload Management, Price Negotiation, Product Samples, and more!
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters  >
        <v-col class="text-center" cols="12" >
          <v-btn large color="green" :to="{name: 'Login', params: {tabName: 'register'}, query: {artist_mode: 'true'}}" :block="$vuetify.breakpoint.xsOnly" class="commission-cta"><v-icon left>palette</v-icon>Open Your Store Now!</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<style scoped>
  .hero-text {
    text-shadow: 2px 2px 5px #000000;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {FormController} from '@/store/forms/form-controller'

@Component
export default class ShieldArtist extends Vue {
  public searchForm: FormController = null as unknown as FormController
  public search() {
    this.searchForm.reset()
    this.searchForm.fields.shield_only.update(true)
    this.$router.push({name: 'SearchProducts', query: this.searchForm.rawData})
  }
  public created() {
    this.searchForm = this.$getForm('search')
  }
}
</script>
