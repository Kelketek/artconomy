<template>
  <ac-load-section :controller="products">
    <v-row class="d-flex" v-if="controls && !store.state.iFrame && !firstProduct && !hideNewButton">
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
                    v-if="!managing && controls && !store.state.iFrame" />
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

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcProductList from '@/components/views/store/AcProductList.vue'
import AcNewProduct from '@/components/views/store/AcNewProduct.vue'
import {flatten} from '@/lib/lib.ts'
import Product from '@/types/Product.ts'
import {mdiCog, mdiPlus} from '@mdi/js'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useStore} from 'vuex'
import {ArtState} from '@/store/artState.ts'


const props = withDefaults(
  defineProps<SubjectiveProps & {mini?: boolean, hideNewButton?: boolean}>(),
  {mini: false, hideNewButton: false},
)
const router = useRouter()
const route = useRoute()
const store = useStore<ArtState>()

const {subjectHandler, isCurrent, controls} = useSubject({ props })
subjectHandler.artistProfile.get()

const url = computed(() => `/api/sales/account/${props.username}/products/`)

const products = useList<Product>(`${flatten(props.username)}-products`, {endpoint: url.value})
products.firstRun()

const showNew = computed({
  get: () => route.query.new === 'true',
  set: (value: boolean) => {
    const query = {...route.query}
    if (value) {
      query.new = 'true'
    } else {
      delete query.new
    }
    router.replace({query})
  }
})

const managing = computed({
  get: () => String(route.name).includes('Manage'),
  set: (val: boolean) => {
    const newRoute = {
      name: String(route.name) + '',
      params: route.params,
      query: route.query,
    }
    if (val && !managing.value) {
      newRoute.name = 'ManageProducts'
    } else if (!val && managing.value) {
      products.get()
      newRoute.name = newRoute.name.replace('Manage', '')
    }
    router.replace(newRoute)
  }
})

const firstProduct = computed(() => isCurrent.value && products.empty)
</script>
