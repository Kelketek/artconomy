<template>
    <v-row no-gutters>
        <v-col cols="12">
            <v-card-text class="text-center">
                Click (or tap) and drag to rearrange your products. Drag onto the 'next' or
                'previous' button to put the submission before or after to shift them into the
                next or previous page. When you are finished, tap the 'finish' button.
            </v-card-text>
        </v-col>
        <v-col cols="12">
            <ac-draggable-list :list="list">
                <template v-slot:default="{sortableList}">
                    <v-col cols="12" sm="3" md="4" lg="3" xl="2"  v-for="product in sortableList" :key="product.x.id">
                        <ac-product-manager :product="product" :username="username"/>
                    </v-col>
                </template>
            </ac-draggable-list>
        </v-col>
    </v-row>
</template>

<style>
.disabled {
    opacity: .5;
}
.page-setter .sortable-ghost {
    display: none;
}
.page-setter .sortable-ghost + .v-card {
    filter: brightness(200%);
}
.page-setter .sortable-ghost + .v-card.disabled {
    filter: brightness(100%);
}
.unavailable {
    opacity: .5;
}
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import draggable from 'vuedraggable'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import {Prop, Watch} from 'vue-property-decorator'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {flatten} from '@/lib/lib'
import {Ratings} from '@/store/profiles/types/Ratings'
import Editable from '@/mixins/editable'
import AcDraggableNavs from '@/components/AcDraggableNavs.vue'
import AcDraggableList from '@/components/AcDraggableList.vue'
import ArtistTag from '@/types/ArtistTag'
import ArtistTagManager from '@/components/views/profile/ArtistTagManager.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import Product from '@/types/Product'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcProductManager from '@/components/views/store/AcProductManager.vue'

@Component({
  components: {
    AcProductManager,
    AcFormDialog,
    AcProductPreview,
    AcDraggableList,
    draggable,
  },
})
export default class ManageProducts extends mixins(Subjective, Editable) {
  @Prop()
  public endpoint!: string

  public get url() {
    return `/api/sales/account/${this.username}/products/manage/`
  }

  public list: ListController<Product> = null as unknown as ListController<Product>
  public created() {
    this.list = this.$getList(`${flatten(this.username)}-products-management`, {endpoint: this.url})
    this.list.firstRun()
  }
}
</script>
