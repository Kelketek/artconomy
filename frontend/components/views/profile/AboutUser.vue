<template>
  <ac-load-section :controller="subjectHandler.user">
    <template v-slot:default>
      <v-container v-if="subject">
        <v-row dense class="fill-height">
          <v-col cols="12" :md="subject.artist_mode ? 4 : 8" order="1">
            <v-card>
              <v-card-text>
                <h2>About {{username}}</h2>
                <v-row v-if="badges" dense>
                  <v-col v-if="subject.stars">
                    <router-link :to="{name: 'Ratings', params: {username}}" v-if="subject.stars">
                      <v-rating :model-value="subject.stars" density="compact" size="small" half-increments color="primary" readonly v-if="subject.stars"/>
                    </router-link>
                  </v-col>
                  <v-col cols="12">
                    <v-chip :color="badge.color" variant="flat" v-for="badge in badges" :key="badge.label" class="mr-1"
                            size="small"
                            :light="badge.light">
                      <strong>{{badge.label}}</strong>
                    </v-chip>
                  </v-col>
                </v-row>
                <small><strong>Views:</strong> {{subject.hits}} <strong>Watchers: </strong>{{subject.watches}}</small>
                <ac-patch-field field-type="ac-editor" :patcher="userHandler.patchers.biography"
                                v-show="editing"
                                v-if="controls"/>
                <div v-show="!editing">
                  <ac-rendered :value="subject.biography" :truncate="true">
                    <template v-slot:empty>
                      <v-col v-if="isCurrent" class="text-center">
                        You haven't added any profile information yet.
                        <v-btn block color="green" @click="() => editing = true" variant="flat">Add some.</v-btn>
                      </v-col>
                    </template>
                  </ac-rendered>
                </div>
                <v-btn block
                       v-if="subjectHandler.artistProfile.x && subject.artist_mode && subjectHandler.artistProfile.x.public_queue"
                       color="secondary"
                       :to="{name: 'Queue', params: {username}}"
                >
                  <v-icon left :icon="mdiTrayFull"/>
                  View Artist Queue
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="8" v-if="subject.artist_mode" order="2" class="justify-center">
            <v-col>
              <ac-subjective-product-list :username="username" :mini="true" :hide-new-button="true"/>
            </v-col>
            <v-col align-self="end">
              <v-btn block color="green" :to="{name: 'Products', params: {username}}" variant="flat">View full store</v-btn>
            </v-col>
          </v-col>
          <v-col cols="12" :md="subject.artist_mode ? 8 : 12" :order="subject.artist_mode ? 2 : 3">
            <v-card>
              <v-card-text>
                <v-card-title>{{username}}'s {{artList.label}}</v-card-title>
                <submission-list
                    :list-name="artList.listName" :endpoint="artList.endpoint" :username="username"
                    :empty-message="artList.emptyMessage" :track-pages="false" :show-pagination="false"
                />
                <v-btn block :to="artList.buttonDest" color="green" class="mt-2" variant="flat">{{artList.buttonText}}</v-btn>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4" :order="subject.artist_mode ? 4 : 2">
            <ac-journals :username="username"/>
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcJournals from '@/components/AcJournals.vue'
import Subjective from '@/mixins/subjective.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcRendered from '@/components/wrappers/AcRendered.ts'
import Editable from '@/mixins/editable.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcSubjectiveProductList from '@/components/views/store/AcSubjectiveProductList.vue'
import AcProductList from '@/components/views/store/AcProductList.vue'
import {flatten} from '@/lib/lib.ts'
import {ListController} from '@/store/lists/controller.ts'
import Product from '@/types/Product.ts'
import Submission from '@/types/Submission.ts'
import SubmissionList from '@/components/views/profile/SubmissionList.vue'
import {User} from '@/store/profiles/types/User.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {mdiTrayFull} from '@mdi/js'

declare interface ProfileBadge {
  label: string,
  color: string,
  light: boolean
}

@Component({
  components: {
    SubmissionList,
    AcProductList,
    AcSubjectiveProductList,
    AcLoadSection,
    AcRendered,
    AcPatchField,
    AcJournals,
  },
})
class AboutUser extends mixins(Subjective, Editable) {
  public products = null as unknown as ListController<Product>
  public art = null as unknown as ListController<Submission>
  public collection = null as unknown as ListController<Submission>
  public mdiTrayFull = mdiTrayFull

  public get badges(): ProfileBadge[] {
    const badges: ProfileBadge[] = []
    if (!this.subjectHandler.artistProfile.x) {
      return badges
    }
    if (this.subjectHandler.artistProfile.x.lgbt) {
      badges.push({
        label: 'LGBTQ+',
        color: 'purple',
        light: false,
      })
    }
    if (this.subjectHandler.artistProfile.x.artist_of_color) {
      badges.push({
        label: 'Artist of Color',
        color: 'orange',
        light: true,
      })
    }
    return badges
  }

  public get userHandler() {
    return this.subjectHandler.user as SingleController<User>
  }

  public get productUrl() {
    return `/api/sales/account/${this.username}/products/`
  }

  public get artList() {
    let buttonText: string
    // eslint-disable-next-line camelcase
    if (this.subject?.artist_mode) {
      if (this.isCurrent) {
        buttonText = 'Manage my art'
      } else {
        buttonText = 'View full gallery'
      }
      return {
        listName: 'art',
        label: 'Art',
        endpoint: `/api/profiles/account/${this.username}/submissions/art/`,
        emptyMessage: 'You have not yet uploaded any art where you are tagged as the artist.',
        buttonText: buttonText,
        buttonDest: {
          name: 'Gallery',
          params: {username: this.username},
        },
      }
    }
    if (this.isCurrent) {
      buttonText = 'Manage my collection'
    } else {
      buttonText = 'View full collection'
    }
    return {
      listName: 'collection',
      label: 'Collection',
      endpoint: `/api/profiles/account/${this.username}/submissions/collection/`,
      emptyMessage: 'You have not uploaded any art to your collection. Your collection ' +
          'holds all art artists have made for you.',
      buttonText: buttonText,
      buttonDest: {
        name: 'Collection',
        params: {username: this.username},
      },
    }
  }

  public created() {
    this.products = this.$getList(`${flatten(this.username)}-products`, {endpoint: this.productUrl})
    // @ts-ignore
    window.about = this
  }
}

export default toNative(AboutUser)
</script>
