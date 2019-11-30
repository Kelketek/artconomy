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
        <h1 class="display-2 font-weight-thin mb-3">Always Open</h1>
        <h2>24/7 Commissions</h2>
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
                      Find an artist <strong>TODAY</strong>. No more hunting through journals and tweets!
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
                  <v-img src="/static/images/fingerpainting.png" max-height="20vh" contain></v-img>
                </v-flex>
                <v-flex xs6 md12 pa-1>
                  <v-layout row justify-content align-center fill-height>
                    <v-flex>
                      <p>Get updates on your commission's progress, with revisions and direct messages.</p>
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
                      Show off your commissions-- make a profile and gallery for your characters!
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
export default class AlwaysOpen extends Vue {
  public searchForm: FormController = null as unknown as FormController
  public search() {
    this.searchForm.reset()
    this.$router.push({name: 'SearchProducts', query: this.searchForm.rawData})
  }
  public created() {
    this.searchForm = this.$getForm('search')
  }
}
</script>
