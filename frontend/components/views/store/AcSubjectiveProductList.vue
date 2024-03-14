<template>
  <ac-load-section :controller="products">
    <v-row class="d-flex" v-if="controls && !$store.state.iFrame && !firstProduct && !hideNewButton">
      <v-col class="text-md-right text-center">
        <v-btn variant="flat" color="green" @click="showNew = true" class="mx-2 d-inline-block" v-if="!managing">
          <v-icon left :icon="mdiPlus"/>
          New Product
        </v-btn>
        <v-btn @click="managing = !managing" color="primary" variant="flat">
          <v-icon left :icon="mdiCog"/>
          <span v-if="managing">Finish</span>
          <span v-else>Manage</span>
        </v-btn>
      </v-col>
    </v-row>
    <ac-product-list :products="products" v-show="!firstProduct" :show-username="false" :mini="mini" v-if="!managing">
      <template v-slot:empty>
        <v-col class="text-center pt-5">
          {{ username }} has no available products.
        </v-col>
      </template>
    </ac-product-list>
    <ac-new-product :username="username" v-model="showNew"
                    v-if="!managing && controls && !$store.state.iFrame"></ac-new-product>
    <v-row no-gutters v-if="firstProduct">
      <v-col cols="12" class="text-md-right text-center">
        <v-btn @click="managing = !managing" color="primary" variant="flat">
          <v-icon left :icon="mdiCog"/>
          <span v-if="managing">Finish</span>
          <span v-else>Manage</span>
        </v-btn>
      </v-col>
      <v-col class="pa-2" cols="12" :lg="mini ? 12 : 8" :offset-lg="mini ? 0 : 2" v-if="!managing">
        <v-card>
          <v-responsive min-height="25vh">
            <v-container class="bg fill-height">
              <v-card-text>
                <v-row no-gutters class="justify-content" align="center">
                  <v-col :cols="mini ? 12 : 6" :class="{'text-center': mini}">
                    <h1>Your art. Your store.</h1>
                    <p>Get started selling commissions by adding a product!</p>
                  </v-col>
                  <v-col class="text-center" :cols="mini ? 12 : 6">
                    <v-btn large variant="flat" color="primary" @click="showNew = true">Add your first product!</v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-container>
          </v-responsive>
        </v-card>
      </v-col>
    </v-row>
    <router-view v-if="managing"/>
  </ac-load-section>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective.ts'
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcProductList from '@/components/views/store/AcProductList.vue'
import AcNewProduct from '@/components/views/store/AcNewProduct.vue'
import {flatten} from '@/lib/lib.ts'
import {ListController} from '@/store/lists/controller.ts'
import Product from '@/types/Product.ts'
import {mdiCog, mdiPlus} from '@mdi/js'

@Component({
  components: {
    AcNewProduct,
    AcProductList,
    AcLoadSection,
  },
})
class AcSubjectiveProductList extends mixins(Subjective) {
  public products: ListController<Product> = null as unknown as ListController<Product>
  public manageProducts: ListController<Product> = null as unknown as ListController<Product>
  @Prop({default: false})
  public mini!: boolean

  @Prop({default: false})
  public hideNewButton!: boolean

  public mdiCog = mdiCog
  public mdiPlus = mdiPlus

  public get showNew(): boolean {
    return this.$route.query.new === 'true'
  }

  public set showNew(value: boolean) {
    const query = {...this.$route.query}
    if (value) {
      query.new = 'true'
    } else {
      delete query.new
    }
    this.$router.replace({query})
  }

  public get managing() {
    return String(this.$route.name).includes('Manage')
  }

  public set managing(val) {
    const route = {
      name: String(this.$route.name) + '',
      params: this.$route.params,
      query: this.$route.query,
    }
    if (val && !this.managing) {
      route.name = 'ManageProducts'
    } else if (!val && this.managing) {
      this.products.get()
      route.name = route.name.replace('Manage', '')
    }
    this.$router.replace(route)
  }

  public get firstProduct() {
    return (
        this.isCurrent &&
        this.products.empty
    )
  }

  public get url() {
    return `/api/sales/account/${this.username}/products/`
  }

  public created() {
    this.products = this.$getList(`${flatten(this.username)}-products`, {endpoint: this.url})
    this.products.firstRun()
    this.manageProducts = this.$getList(`${flatten(this.username)}-products-manage`, {endpoint: `${this.url}manage/`})
    this.subjectHandler.artistProfile.get()
  }
}

export default toNative(AcSubjectiveProductList)
</script>
