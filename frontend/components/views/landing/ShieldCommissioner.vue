<template>
  <v-container fluid class="pa-0">
    <v-img src="/static/images/banner.jpg" :aspect-ratio="16/9" max-height="250px">
      <v-layout
        align-center
        column
        justify-center
        fill-height
        class="hero-text"
      >
        <h1 class="display-2 font-weight-thin mb-3">Ready Artists</h1>
        <h2>Guaranteed Completion</h2>
      </v-layout>
    </v-img>
    <v-container>
      <v-layout row wrap class="py-2">
        <v-flex xs12 md4 text-xs-center d-flex>
          <v-layout row>
            <v-flex grow pa-1>
              <v-layout row wrap>
                <v-flex xs6 md12 order-xs2 order-md1>
                  <v-img src="/static/images/laptop.png" max-height="20vh" contain></v-img>
                </v-flex>
                <v-flex xs6 md12 order-xs1 order-md2>
                  <v-layout row justify-content align-center fill-height>
                    <v-flex pa-1>
                      Select one of our many artists to commission. We're always open!
                    </v-flex>
                  </v-layout>
                </v-flex>
              </v-layout>
            </v-flex>
            <v-flex shrink class="hidden-sm-and-down">
              <v-divider vertical></v-divider>
            </v-flex>
          </v-layout>
        </v-flex>
        <v-flex xs12 md4 text-xs-center d-flex>
          <v-layout row>
            <v-flex grow pa-1>
              <v-layout row wrap>
                <v-flex xs6 md12>
                  <v-img src="/static/images/403.png" max-height="20vh" contain></v-img>
                </v-flex>
                <v-flex xs6 md12 pa-1>
                  <v-layout row justify-content align-center fill-height>
                    <v-flex>
                      <p><strong>Never get scammed.</strong> With <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>, your artist's work is guaranteed, and you are always protected.</p>
                    </v-flex>
                  </v-layout>
                </v-flex>
              </v-layout>
            </v-flex>
            <v-flex shrink class="hidden-sm-and-down">
              <v-divider vertical></v-divider>
            </v-flex>
          </v-layout>
        </v-flex>
        <v-flex xs12 md4 text-xs-center d-flex>
          <v-layout row>
            <v-flex grow pa-1>
              <v-layout row wrap>
                <v-flex xs6 md12 order-xs2 order-md1>
                  <v-img src="/static/images/fridge.png" max-height="20vh" contain></v-img>
                </v-flex>
                <v-flex xs6 md12 pa-1 order-xs1 order-md2>
                  <v-layout row justify-content align-center fill-height>
                    <v-flex>
                      Catalog your pieces and characters. Show us what you got!
                    </v-flex>
                  </v-layout>
                </v-flex>
              </v-layout>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout>
      <v-layout row wrap>
        <v-flex xs12 text-xs-center>
          <v-btn large color="green" @click="search" :block="$vuetify.breakpoint.xsOnly" class="commission-cta"><v-icon left>palette</v-icon>Commission an Artist Now!</v-btn>
        </v-flex>
      </v-layout>
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
export default class ShieldCommissioner extends Vue {
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