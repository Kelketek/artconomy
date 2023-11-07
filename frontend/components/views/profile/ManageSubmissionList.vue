<template>
  <v-row no-gutters>
    <v-col cols="12">
      <v-card-text class="text-center">
        Click (or tap) and drag to rearrange your submissions. Drag onto the 'next' or
        'previous' button to put the submission before or after to shift them into the
        next or previous page. When you are finished, tap the 'finish' button.
      </v-card-text>
    </v-col>
    <v-col cols="12">
      <ac-draggable-list :list="list">
        <template v-slot:default="{sortableList}">
          <v-col cols="4" sm="3" lg="2" v-for="submission in sortableList" :key="submission.x.id">
            <ac-gallery-preview class="pa-1" @click.capture.stop.prevent="() => false"
                                :linked="false"
                                :submission="submission.x" :show-footer="true">
            </ac-gallery-preview>
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
</style>

<script lang="ts">
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective'
import draggable from 'vuedraggable'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {flatten} from '@/lib/lib'
import {Ratings} from '@/store/profiles/types/Ratings'
import Editable from '@/mixins/editable'
import AcDraggableNavs from '@/components/AcDraggableNavs.vue'
import AcDraggableList from '@/components/AcDraggableList.vue'

@Component({
  components: {
    AcDraggableList,
    AcDraggableNavs,
    AcPaginated,
    AcGalleryPreview,
    AcLoadSection,
    draggable,
  },
})
class ManageSubmissionList extends mixins(Subjective, Editable) {
  @Prop()
  public listName!: string

  @Prop()
  public endpoint!: string

  @Watch('rawRating')
  public refreshListing(newValue: Ratings, oldValue: Ratings | undefined) {
    if (oldValue === undefined) {
      return
    }
    this.list.get()
  }

  public list: ListController<Submission> = null as unknown as ListController<Submission>

  public created() {
    let listName = this.listName
    if (this.username) {
      listName = `${flatten(this.username)}-${listName}-management`
    }
    this.list = this.$getList(listName, {endpoint: this.endpoint})
  }
}

export default toNative(ManageSubmissionList)
</script>
