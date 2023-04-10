<template>
  <v-container fluid class="pa-0">
    <router-view v-if="!currentRoute" />
    <v-container v-else>
      <ac-profile-header :username="username" v-if="!iFrame" />
      <ac-subjective-product-list :username="username"/>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import AcProductList from '@/components/views/store/AcProductList.vue'
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcBankToggle from '@/components/fields/AcBankToggle.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import AcNewProduct from '@/components/views/store/AcNewProduct.vue'
import AcSubjectiveProductList from '@/components/views/store/AcSubjectiveProductList.vue'
import {State} from 'vuex-class'
  @Component({
    components: {
      AcSubjectiveProductList,
      AcNewProduct,
      AcBoundField,
      AcPatchField,
      AcBankToggle,
      AcLoadSection,
      AcFormDialog,
      AcProfileHeader,
      AcProductList,
    },
  })
export default class Store extends mixins(Subjective) {
    @State('iFrame') public iFrame!: boolean

    public get currentRoute() {
      return ['Store', 'StoreiFrame', 'ManageStore'].indexOf(this.$route.name + '') !== -1
    }
}
</script>
