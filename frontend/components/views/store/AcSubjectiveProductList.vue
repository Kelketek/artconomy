<template>
  <ac-load-section :controller="products">
    <ac-product-list :products="products" v-show="!firstProduct"></ac-product-list>
    <ac-add-button v-model="showNew" v-if="controls && !iFrame">New Product</ac-add-button>
    <ac-new-product :username="username" v-model="showNew" v-if="controls && !iFrame"></ac-new-product>
    <v-row no-gutters   v-if="firstProduct">
      <v-col class="pa-2" cols="12" lg="8" offset-lg="2" >
        <v-card>
          <v-responsive min-height="25vh">
            <v-container class="bg fill-height" >
              <v-card-text>
                <v-row no-gutters class="justify-content"   align="center">
                  <v-col>
                    <h1>Your art. Your store.</h1>
                    <p>Get started selling commissions by adding a product!</p>
                  </v-col>
                  <v-col class="text-center" >
                    <v-btn large color="primary" @click="showNew = true">Add your first product!</v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-container>
          </v-responsive>
        </v-card>
      </v-col>
    </v-row>
  </ac-load-section>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcProductList from '@/components/views/store/AcProductList.vue'
import AcNewProduct from '@/components/views/store/AcNewProduct.vue'
import AcAddButton from '@/components/AcAddButton.vue'
import {flatten} from '@/lib'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import {State} from 'vuex-class'
  @Component({
    components: {AcAddButton, AcNewProduct, AcProductList, AcLoadSection},
  })
export default class AcSubjectiveProductList extends mixins(Subjective) {
    @State('iFrame') public iFrame!: boolean
    public products: ListController<Product> = null as unknown as ListController<Product>
    public showNew = false
    public get firstProduct() {
      return (
        this.isCurrent &&
        this.products.empty
      )
    }
    public get url() {
      return `/api/sales/v1/account/${this.username}/products/`
    }
    public created() {
      this.products = this.$getList(flatten(`${this.username}-products`), {endpoint: this.url})
      this.products.firstRun()
      this.subjectHandler.artistProfile.get()
    }
}
</script>
